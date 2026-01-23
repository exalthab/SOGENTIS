# dashboard/views/admin/moderation.py
from __future__ import annotations

from django.apps import apps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, FieldError
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, QuerySet
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from dashboard.permissions import is_admin, is_staff_user


# =========================
# Permissions
# =========================
def _is_staff_or_admin(user) -> bool:
    return bool(is_admin(user) or is_staff_user(user))


# =========================
# Model loader (safe)
# =========================
def _get_registration_application_model():
    try:
        return apps.get_model("accounts_users", "RegistrationApplication")
    except Exception:
        return None


def _safe_select_related(qs: QuerySet) -> QuerySet:
    try:
        return qs.select_related("user")
    except Exception:
        return qs


def _safe_prefetch_docs(qs: QuerySet) -> QuerySet:
    # RegistrationApplication.documents (related_name="documents") — si existe
    try:
        return qs.prefetch_related("documents")
    except Exception:
        return qs


def _apply_filters(qs: QuerySet, q: str, category: str) -> QuerySet:
    if category:
        try:
            qs = qs.filter(category=category)
        except Exception:
            pass

    if q:
        # Recherche robuste : user.email / user.username / (optionnel) user.profile.first_name/last_name
        base_q = (
            Q(user__email__icontains=q)
            | Q(user__username__icontains=q)
        )
        try:
            # si ton UserProfile unifié est lié via related_name="profile"
            base_q |= Q(user__profile__first_name__icontains=q) | Q(user__profile__last_name__icontains=q)
        except Exception:
            pass

        try:
            qs = qs.filter(base_q)
        except FieldError:
            # fallback minimal si certains champs n'existent pas
            qs = qs.filter(Q(user__email__icontains=q) | Q(user__username__icontains=q))
        except Exception:
            pass

    return qs


# ======================================================
# Views
# ======================================================
@login_required
def admin_moderation_view(request):
    """
    Vue Modération:
    - liste des RegistrationApplication en PENDING
    - filtres ?q= & ?category=
    - pagination ?page=
    Rend: templates/dashboard/admin/moderation.html
    """
    if not _is_staff_or_admin(request.user):
        raise PermissionDenied

    AppModel = _get_registration_application_model()

    q = (request.GET.get("q") or "").strip()
    category = (request.GET.get("category") or "").strip()
    page = (request.GET.get("page") or "1").strip()

    applications = []
    page_obj = None
    paginator = None

    if AppModel is None:
        messages.error(request, _("Modèle RegistrationApplication introuvable."))
    else:
        qs = AppModel.objects.filter(status="PENDING")
        qs = _safe_select_related(qs)
        qs = _safe_prefetch_docs(qs)
        qs = _apply_filters(qs, q=q, category=category)

        # ordering robuste
        try:
            qs = qs.order_by("created_at")
        except Exception:
            qs = qs.order_by("id")

        paginator = Paginator(qs, 25)
        page_obj = paginator.get_page(page)
        applications = page_obj.object_list

    context = {
        "page_title": _("Modération"),
        "profile_model_available": bool(AppModel),  # ✅ ton template utilise ce nom
        "applications": applications,               # ✅ ton template boucle sur applications
        "q": q,
        "category": category,
        "page_obj": page_obj,
        "paginator": paginator,
        "is_paginated": bool(page_obj and page_obj.has_other_pages()),
    }
    return render(request, "dashboard/admin/moderation.html", context)


@login_required
def admin_application_approve_view(request, pk: int):
    """
    POST only:
    - status -> APPROVED
    - trace payload.moderation
    - active user (best effort)
    """
    if request.method != "POST":
        return redirect("dashboard:admin:moderation")

    if not _is_staff_or_admin(request.user):
        raise PermissionDenied

    AppModel = _get_registration_application_model()
    if AppModel is None:
        messages.error(request, _("Modèle RegistrationApplication introuvable."))
        return redirect("dashboard:admin:moderation")

    with transaction.atomic():
        qs = AppModel.objects.select_for_update()
        app = get_object_or_404(qs, pk=pk)

        if getattr(app, "status", "") != "PENDING":
            messages.info(request, _("Cette demande n’est plus en attente."))
            return redirect("dashboard:admin:moderation")

        app.status = "APPROVED"

        # trace dans payload (robuste)
        try:
            payload = dict(getattr(app, "payload", {}) or {})
            payload["moderation"] = {
                **(payload.get("moderation") or {}),
                "approved_at": timezone.now().isoformat(),
                "approved_by": getattr(request.user, "pk", None),
            }
            app.payload = payload
        except Exception:
            pass

        # best effort: activer l'utilisateur
        user = getattr(app, "user", None)
        if user is not None and hasattr(user, "is_active"):
            try:
                if not bool(getattr(user, "is_active", False)):
                    user.is_active = True
                    user.save(update_fields=["is_active"])
            except Exception:
                pass

        update_fields = ["status", "payload"]
        if hasattr(app, "updated_at"):
            update_fields.append("updated_at")
        app.save(update_fields=update_fields)

    messages.success(request, _("Demande approuvée."))
    return redirect("dashboard:admin:moderation")


@login_required
def admin_application_reject_view(request, pk: int):
    """
    POST only:
    - status -> REJECTED
    - trace payload.moderation (+ note)
    """
    if request.method != "POST":
        return redirect("dashboard:admin:moderation")

    if not _is_staff_or_admin(request.user):
        raise PermissionDenied

    AppModel = _get_registration_application_model()
    if AppModel is None:
        messages.error(request, _("Modèle RegistrationApplication introuvable."))
        return redirect("dashboard:admin:moderation")

    note = (request.POST.get("note") or "").strip()

    with transaction.atomic():
        qs = AppModel.objects.select_for_update()
        app = get_object_or_404(qs, pk=pk)

        if getattr(app, "status", "") != "PENDING":
            messages.info(request, _("Cette demande n’est plus en attente."))
            return redirect("dashboard:admin:moderation")

        app.status = "REJECTED"

        try:
            payload = dict(getattr(app, "payload", {}) or {})
            payload["moderation"] = {
                **(payload.get("moderation") or {}),
                "rejected_at": timezone.now().isoformat(),
                "rejected_by": getattr(request.user, "pk", None),
                "note": note,
            }
            app.payload = payload
        except Exception:
            pass

        update_fields = ["status", "payload"]
        if hasattr(app, "updated_at"):
            update_fields.append("updated_at")
        app.save(update_fields=update_fields)

    messages.success(request, _("Demande refusée."))
    return redirect("dashboard:admin:moderation")






# # dashboard/views/admin/moderation.py
# from __future__ import annotations

# from django.apps import apps
# from django.contrib.auth.decorators import login_required
# from django.core.exceptions import PermissionDenied
# from django.core.paginator import Paginator
# from django.db.models import QuerySet
# from django.shortcuts import render
# from django.utils.translation import gettext_lazy as _

# from dashboard.permissions import is_admin, is_staff_user


# def _is_staff_or_admin(user) -> bool:
#     return bool(is_admin(user) or is_staff_user(user))


# def _safe_model(app_label: str, model_name: str):
#     try:
#         return apps.get_model(app_label, model_name)
#     except Exception:
#         return None


# def _get_profile_model():
#     """
#     Essaie plusieurs modèles possibles sans casser si un n'existe pas.
#     Ajuste si tu connais le bon modèle “source of truth”.
#     """
#     candidates = [
#         ("accounts_users", "UserProfile"),
#         ("accounts_users", "SocialProfile"),
#         ("accounts_users", "UserEconomicProfile"),
#     ]
#     for app_label, model_name in candidates:
#         m = _safe_model(app_label, model_name)
#         if m:
#             return m
#     return None


# def _field_names(model) -> set[str]:
#     try:
#         return {f.name for f in model._meta.get_fields()}
#     except Exception:
#         return set()


# def _pending_queryset(ProfileModel) -> QuerySet:
#     """
#     Construit un queryset "pending" selon les champs réellement présents.
#     """
#     fields = _field_names(ProfileModel)

#     qs = ProfileModel.objects.all()

#     # status/validation_status
#     if "status" in fields:
#         # supporte pending / PENDING / etc.
#         return qs.filter(status__in=["pending", "PENDING", "Pending"])
#     if "validation_status" in fields:
#         return qs.filter(validation_status__in=["pending", "PENDING", "Pending"])

#     # bool flags
#     if "is_validated" in fields:
#         return qs.filter(is_validated=False)
#     if "is_approved" in fields:
#         return qs.filter(is_approved=False)

#     # fallback: rien
#     return qs.none()


# @login_required
# def admin_moderation_view(request):
#     """
#     Modération globale (prod):
#     - profils en attente (si supportés)
#     """
#     if not _is_staff_or_admin(request.user):
#         raise PermissionDenied

#     ProfileModel = _get_profile_model()
#     pending_profiles = []
#     page_obj = None
#     paginator = None

#     if ProfileModel is not None:
#         qs = _pending_queryset(ProfileModel)

#         fields = _field_names(ProfileModel)
#         select_fields = []
#         if "user" in fields:
#             select_fields.append("user")
#         if "membership_role" in fields:
#             select_fields.append("membership_role")
#         if "role" in fields:
#             select_fields.append("role")

#         if select_fields:
#             try:
#                 qs = qs.select_related(*select_fields)
#             except Exception:
#                 pass

#         # ordering safe
#         if "created_at" in fields:
#             qs = qs.order_by("created_at")
#         else:
#             qs = qs.order_by("id")

#         paginator = Paginator(qs, 25)
#         page_obj = paginator.get_page((request.GET.get("page") or "1").strip())
#         pending_profiles = page_obj.object_list

#     context = {
#         "page_title": _("Modération"),
#         "pending_profiles": pending_profiles,
#         "profile_model_available": bool(ProfileModel),
#         "page_obj": page_obj,
#         "paginator": paginator,
#         "is_paginated": bool(page_obj and page_obj.has_other_pages()),
#     }
#     return render(request, "dashboard/admin/moderation.html", context)








# # dashboard/views/admin/moderation.py 
# from django.contrib.auth.decorators import login_required
# from django.core.exceptions import PermissionDenied
# from django.shortcuts import render
# from django.utils.translation import gettext_lazy as _

# from dashboard.permissions import is_admin, is_staff_user

# try:
#     # ⚠️ mets ici le BON modèle de profil qui est utilisé pour validation
#     # ex: accounts_users.models.users_profile.UserProfile (social)
#     from accounts_users.models.users_profile import UserProfile
# except Exception:
#     UserProfile = None


# def _is_staff_or_admin(user):
#     return is_admin(user) or is_staff_user(user)


# @login_required
# def admin_moderation_view(request):
#     """
#     Modération globale:
#     - profils en attente (si supporté par le modèle)
#     """
#     if not _is_staff_or_admin(request.user):
#         raise PermissionDenied

#     pending_profiles = []

#     if UserProfile is not None:
#         # ✅ filtre seulement si le champ existe réellement
#         profile_fields = {f.name for f in UserProfile._meta.get_fields()}

#         if "status" in profile_fields:
#             qs = UserProfile.objects.filter(status="pending")
#         elif "is_validated" in profile_fields:
#             qs = UserProfile.objects.filter(is_validated=False)
#         elif "is_approved" in profile_fields:
#             qs = UserProfile.objects.filter(is_approved=False)
#         else:
#             qs = UserProfile.objects.none()

#         # ✅ select_related seulement si relation existe
#         select_related_fields = ["user"]
#         if "membership_role" in profile_fields:
#             select_related_fields.append("membership_role")

#         pending_profiles = qs.select_related(*select_related_fields).order_by("created_at")

#     context = {
#         "page_title": _("Modération"),
#         "pending_profiles": pending_profiles,
#     }
#     return render(request, "dashboard/admin/moderation.html", context)






# # dashboard/views/admin/moderation.py
# from django.contrib.auth.decorators import login_required
# from django.core.exceptions import PermissionDenied
# from django.shortcuts import render
# from django.utils.translation import gettext_lazy as _

# from dashboard.permissions import is_admin, is_staff_user

# try:
#     from accounts_users.models.users_profile import UserProfile
# except Exception:
#     UserProfile = None


# def _is_staff_or_admin(user):
#     return is_admin(user) or is_staff_user(user)


# @login_required
# def admin_moderation_view(request):
#     """
#     Écran de modération globale :
#     - profils en attente
#     - prêt à accueillir signalements / logs plus tard
#     """
#     user = request.user
#     if not _is_staff_or_admin(user):
#         raise PermissionDenied

#     pending_profiles = []
#     if UserProfile is not None:
#         pending_profiles = (
#             UserProfile.objects.filter(status="pending")
#             .select_related("user", "membership_role")
#             .order_by("created_at")
#         )

#     context = {
#         "page_title": _("Modération"),
#         "pending_profiles": pending_profiles,
#     }
#     return render(request, "dashboard/admin/moderation.html", context)





# from django.contrib.auth.decorators import login_required, user_passes_test
# from django.shortcuts import render
# from dashboard.permissions import is_admin


# @login_required
# @user_passes_test(is_admin)
# def moderation_dashboard(request):
#     return render(request, "dashboard/admin/moderation.html")
