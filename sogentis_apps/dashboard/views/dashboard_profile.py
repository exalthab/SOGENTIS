# dashboard/views/dashboard_profile.py
from __future__ import annotations

from typing import Any, Optional, Tuple

from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import FieldDoesNotExist
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _

from dashboard.views.utils import (
    breadcrumb,
    safe_reverse,
    get_user_profile,
    iter_user_profiles,
    detect_profile_kind,
    pick_profile_display_values,
)


# ======================================================
# Safe model helpers
# ======================================================
def _model_has_field(model, name: str) -> bool:
    try:
        model._meta.get_field(name)
        return True
    except FieldDoesNotExist:
        return False
    except Exception:
        return False


# ======================================================
# User form (dynamic)
# ======================================================
def _pick_user_fields(UserModel) -> tuple[str, ...]:
    candidates = ("first_name", "last_name", "username", "email")
    return tuple(f for f in candidates if _model_has_field(UserModel, f))


def _build_user_form():
    UserModel = get_user_model()
    picked_fields = _pick_user_fields(UserModel)

    class UserUpdateForm(forms.ModelForm):
        class Meta:
            model = UserModel
            fields = picked_fields

    return UserUpdateForm


# ======================================================
# Profile selection logic
# ======================================================
def _select_profile(user, preferred: str = "") -> Tuple[Optional[Any], str]:
    """
    Retourne (profile, kind) avec kind in {"economic","social","generic"}.
    """
    preferred = (preferred or "").strip().lower()

    try:
        profiles = iter_user_profiles(user)
    except Exception:
        profiles = []

    if preferred in {"social", "economic", "generic"}:
        for p in profiles:
            if detect_profile_kind(p) == preferred:
                return p, preferred

        p = get_user_profile(user)
        return (p, detect_profile_kind(p)) if p else (None, "generic")

    p = get_user_profile(user)
    if p:
        return p, detect_profile_kind(p)

    if profiles:
        p = profiles[0]
        return p, detect_profile_kind(p)

    return None, "generic"


# ======================================================
# Profile form (dynamic)
# ======================================================
def _build_profile_form(profile: Any):
    candidates = (
        "phone_number", "phone", "mobile", "tel",
        "country", "country_of_residence", "residence_country",
        "city", "city_of_residence", "residence_city",
        "address", "address_line1", "address_line2",
        "profession", "function", "job_title",
        "avatar", "photo", "profile_picture",
    )

    fields_list = [
        f for f in candidates
        if _model_has_field(profile.__class__, f)
    ]

    class ProfileUpdateDynamicForm(forms.ModelForm):
        class Meta:
            model = profile.__class__
            fields = tuple(dict.fromkeys(fields_list))  # déduplication safe

    return ProfileUpdateDynamicForm


# ======================================================
# Views
# ======================================================
@login_required
def dashboard_profile_view(request):
    preferred = (request.GET.get("kind") or "").strip().lower()
    profile, profile_kind = _select_profile(request.user, preferred)

    base_ctx = {
        "page_title": _("Mon profil"),
        "topbar_title": _("Mon profil"),
        "topbar_subtitle": _("Consultez vos informations et votre statut."),
        "breadcrumbs": breadcrumb(
            (_("Dashboard"), safe_reverse("dashboard:hub")),
            (_("Profil"), None),
        ),
    }

    if not profile:
        messages.info(
            request,
            _("Aucun profil n’est encore renseigné. Vous pouvez le compléter.")
        )
        return render(
            request,
            "dashboard/profile/profile.html",
            {
                **base_ctx,
                "profile": None,
                "profile_kind": "generic",
                "profile_status": "",
                "profile_phone": "—",
                "profile_country": "—",
                "profile_city": "—",
            },
        )

    return render(
        request,
        "dashboard/profile/profile.html",
        {
            **base_ctx,
            "profile": profile,
            "profile_kind": profile_kind,
            **pick_profile_display_values(profile),
        },
    )


@login_required
def dashboard_profile_edit_view(request):
    preferred = (request.GET.get("kind") or "").strip().lower()
    profile, profile_kind = _select_profile(request.user, preferred)

    if not profile:
        messages.warning(
            request,
            _("Aucun profil n’est associé à ce compte pour le moment.")
        )
        return redirect("dashboard:hub")

    base_ctx = {
        "page_title": _("Modifier le profil"),
        "topbar_title": _("Modifier le profil"),
        "topbar_subtitle": _("Mettez à jour vos informations."),
        "topbar_actions": f"""
          <a class="btn btn-outline-primary btn-sm"
             href="{safe_reverse('dashboard:profile')}">
            <i class="fas fa-eye me-1" aria-hidden="true"></i>
            {_('Voir')}
          </a>
        """,
        "breadcrumbs": breadcrumb(
            (_("Dashboard"), safe_reverse("dashboard:hub")),
            (_("Profil"), safe_reverse("dashboard:profile")),
            (_("Modifier"), None),
        ),
        "title": _("Modifier le profil"),
    }

    UserForm = _build_user_form()
    user_form = UserForm(request.POST or None, instance=request.user)

    try:
        from dashboard.forms.profile_form import ProfileUpdateForm  # type: ignore
        ProfileForm = ProfileUpdateForm
    except Exception:
        ProfileForm = _build_profile_form(profile)

    profile_form = ProfileForm(
        request.POST or None,
        request.FILES or None,
        instance=profile,
    )

    if request.method == "POST":
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, _("Profil mis à jour avec succès."))
            return redirect("dashboard:profile")
        messages.error(request, _("Veuillez corriger les erreurs du formulaire."))

    return render(
        request,
        "dashboard/profile/profile_edit.html",
        {
            **base_ctx,
            "profile": profile,
            "profile_kind": profile_kind,
            "user_form": user_form,
            "form": profile_form,
            **pick_profile_display_values(profile),
        },
    )






# # dashboard/views/dashboard_profile.py
# from __future__ import annotations

# from typing import Any, Optional, Tuple

# from django import forms
# from django.contrib import messages
# from django.contrib.auth import get_user_model
# from django.contrib.auth.decorators import login_required
# from django.core.exceptions import FieldDoesNotExist
# from django.shortcuts import redirect, render
# from django.utils.translation import gettext_lazy as _

# from dashboard.views.utils import (
#     breadcrumb,
#     safe_reverse,
#     get_user_profile,
#     iter_user_profiles,
#     detect_profile_kind,
#     pick_profile_display_values,
# )


# # ======================================================
# # Safe model helpers
# # ======================================================
# def _model_has_field(model, name: str) -> bool:
#     try:
#         model._meta.get_field(name)
#         return True
#     except FieldDoesNotExist:
#         return False
#     except Exception:
#         return False


# # ======================================================
# # User form (dynamic)
# # ======================================================
# def _pick_user_fields(UserModel) -> tuple[str, ...]:
#     candidates = ("first_name", "last_name", "username", "email")
#     fields = [f for f in candidates if _model_has_field(UserModel, f)]
#     return tuple(fields) if fields else tuple()


# def _build_user_form():
#     UserModel = get_user_model()
#     picked_fields = _pick_user_fields(UserModel)

#     class UserUpdateForm(forms.ModelForm):
#         class Meta:
#             model = UserModel
#             fields = picked_fields

#     return UserUpdateForm


# # ======================================================
# # Profile selection logic
# # ======================================================
# def _select_profile(user, preferred: str = "") -> Tuple[Optional[Any], str]:
#     """
#     Retourne (profile, kind) avec kind in {"economic","social","generic"}.

#     Règles:
#     - Si preferred fourni, on essaye de trouver un profil de ce type via iter_user_profiles().
#     - Sinon, on renvoie le profil "principal" (get_user_profile()).
#     - Fallback ultime : premier profil trouvé.
#     """
#     preferred = (preferred or "").strip().lower()

#     profiles = []
#     try:
#         profiles = iter_user_profiles(user)
#     except Exception:
#         profiles = []

#     # 1) preferred explicite
#     if preferred in {"social", "economic", "generic"}:
#         for p in profiles:
#             if detect_profile_kind(p) == preferred:
#                 return p, preferred

#         p = get_user_profile(user)
#         if p:
#             return p, detect_profile_kind(p)
#         return None, "generic"

#     # 2) profil principal
#     p = get_user_profile(user)
#     if p:
#         return p, detect_profile_kind(p)

#     # 3) fallback : premier profil trouvé
#     if profiles:
#         p2 = profiles[0]
#         return p2, detect_profile_kind(p2)

#     return None, "generic"


# # ======================================================
# # Profile form (dynamic)
# # ======================================================
# def _build_profile_form(profile: Any):
#     """
#     Form dynamique basé sur les champs existants sur le modèle du profil.
#     """
#     candidates = (
#         "phone_number", "phone", "mobile", "tel",
#         "country", "country_of_residence", "residence_country",
#         "city", "city_of_residence", "residence_city",
#         "address", "address_line1", "address_line2",
#         "profession", "function", "job_title",
#         "avatar", "photo", "profile_picture",
#     )

#     fields_list: list[str] = []
#     for f in candidates:
#         if _model_has_field(profile.__class__, f) and f not in fields_list:
#             fields_list.append(f)

#     class ProfileUpdateDynamicForm(forms.ModelForm):
#         class Meta:
#             model = profile.__class__
#             fields = tuple(fields_list) if fields_list else tuple()

#     return ProfileUpdateDynamicForm


# # ======================================================
# # Views
# # ======================================================
# @login_required
# def dashboard_profile_view(request):
#     preferred = (request.GET.get("kind") or "").strip().lower()
#     profile, profile_kind = _select_profile(request.user, preferred=preferred)

#     # ✅ IMPORTANT: page_title garanti (fix topbar)
#     base_ctx = {
#         "page_title": _("Mon profil"),
#         "topbar_title": _("Mon profil"),
#         "topbar_subtitle": "",
#         "breadcrumbs": breadcrumb(
#             (_("Dashboard"), safe_reverse("dashboard:hub")),
#             (_("Profil"), None),
#         ),
#     }

#     # ✅ Ne pas bloquer si pas de profil
#     if not profile:
#         messages.info(request, _("Aucun profil n’est encore renseigné. Vous pouvez le compléter."))
#         return render(
#             request,
#             "dashboard/profile/profile.html",
#             {
#                 **base_ctx,
#                 "profile": None,
#                 "profile_kind": "generic",
#                 "profile_status": "",
#                 "profile_phone": "—",
#                 "profile_country": "—",
#                 "profile_city": "—",
#             },
#         )

#     pv = pick_profile_display_values(profile)

#     return render(
#         request,
#         "dashboard/profile/profile.html",
#         {
#             **base_ctx,
#             "profile": profile,
#             "profile_kind": profile_kind,
#             **pv,
#         },
#     )


# @login_required
# def dashboard_profile_edit_view(request):
#     preferred = (request.GET.get("kind") or "").strip().lower()
#     profile, profile_kind = _select_profile(request.user, preferred=preferred)

#     # ✅ page_title garanti (fix topbar)
#     base_ctx = {
#         "page_title": _("Modifier le profil"),
#         "topbar_title": _("Modifier le profil"),
#         "topbar_subtitle": "",
#         "breadcrumbs": breadcrumb(
#             (_("Dashboard"), safe_reverse("dashboard:hub")),
#             (_("Profil"), safe_reverse("dashboard:profile")),
#             (_("Modifier"), None),
#         ),
#         "title": _("Modifier le profil"),
#     }

#     if not profile:
#         messages.warning(request, _("Aucun profil n’est associé à ce compte pour le moment."))
#         return redirect("dashboard:hub")

#     UserForm = _build_user_form()
#     user_form = UserForm(request.POST or None, instance=request.user)

#     # 1) si custom form existe -> on l’utilise
#     try:
#         from dashboard.forms.profile_form import ProfileUpdateForm  # type: ignore
#         ProfileForm = ProfileUpdateForm
#     except Exception:
#         # 2) sinon, fallback dynamique safe
#         ProfileForm = _build_profile_form(profile)

#     profile_form = ProfileForm(
#         request.POST or None,
#         request.FILES or None,
#         instance=profile,
#     )

#     if request.method == "POST":
#         if user_form.is_valid() and profile_form.is_valid():
#             user_form.save()
#             profile_form.save()
#             messages.success(request, _("Profil mis à jour avec succès."))
#             return redirect("dashboard:profile")

#         messages.error(request, _("Veuillez corriger les erreurs du formulaire."))

#     pv = pick_profile_display_values(profile)

#     return render(
#         request,
#         "dashboard/profile/profile_edit.html",
#         {
#             **base_ctx,
#             "profile": profile,
#             "profile_kind": profile_kind,
#             "user_form": user_form,
#             "form": profile_form,
#             **pv,
#         },
#     )






# # dashboard/views/dashboard_profile.py
# from __future__ import annotations

# from typing import Any, Optional, Tuple

# from django import forms
# from django.contrib import messages
# from django.contrib.auth import get_user_model
# from django.contrib.auth.decorators import login_required
# from django.core.exceptions import FieldDoesNotExist
# from django.shortcuts import redirect, render
# from django.utils.translation import gettext_lazy as _

# from dashboard.views.utils import (
#     breadcrumb,
#     safe_reverse,
#     get_user_profile,
#     iter_user_profiles,
#     detect_profile_kind,
#     pick_profile_display_values,
# )


# # ======================================================
# # Safe model helpers
# # ======================================================
# def _model_has_field(model, name: str) -> bool:
#     try:
#         model._meta.get_field(name)
#         return True
#     except FieldDoesNotExist:
#         return False
#     except Exception:
#         return False


# # ======================================================
# # User form (dynamic)
# # ======================================================
# def _pick_user_fields(UserModel) -> tuple[str, ...]:
#     candidates = ("first_name", "last_name", "username", "email")
#     fields = [f for f in candidates if _model_has_field(UserModel, f)]
#     return tuple(fields) if fields else tuple()


# def _build_user_form():
#     UserModel = get_user_model()
#     picked_fields = _pick_user_fields(UserModel)

#     class UserUpdateForm(forms.ModelForm):
#         class Meta:
#             model = UserModel
#             fields = picked_fields

#     return UserUpdateForm


# # ======================================================
# # Profile selection logic
# # ======================================================
# def _select_profile(user, preferred: str = "") -> Tuple[Optional[Any], str]:
#     """
#     Retourne (profile, kind) avec kind in {"economic","social","generic"}.

#     Règles:
#     - Si preferred fourni, on essaye de trouver un profil de ce type.
#     - Sinon, on renvoie le profil "principal" (get_user_profile),
#       mais on garde aussi une fallback via iter_user_profiles pour éviter les surprises.
#     """
#     preferred = (preferred or "").strip().lower()
#     profiles = []
#     try:
#         profiles = iter_user_profiles(user)
#     except Exception:
#         profiles = []

#     # 1) Si preferred: trouver un profil de ce kind
#     if preferred in {"social", "economic", "generic"}:
#         for p in profiles:
#             if detect_profile_kind(p) == preferred:
#                 return p, preferred

#         # fallback: certains projets n'ont qu'un profile central
#         p = get_user_profile(user)
#         if p:
#             return p, detect_profile_kind(p)
#         return None, "generic"

#     # 2) Par défaut: profil principal
#     p = get_user_profile(user)
#     if p:
#         return p, detect_profile_kind(p)

#     # 3) fallback ultime: premier profil trouvé
#     if profiles:
#         p2 = profiles[0]
#         return p2, detect_profile_kind(p2)

#     return None, "generic"


# # ======================================================
# # Profile form (dynamic)
# # ======================================================
# def _build_profile_form(profile: Any):
#     """
#     Form dynamique basé sur les champs existants sur le modèle du profil.
#     """
#     # Champs usuels (social + economic + generic)
#     candidates = (
#         "phone_number", "phone", "mobile", "tel",
#         "country", "country_of_residence", "residence_country",
#         "city", "city_of_residence", "residence_city",
#         "address", "address_line1", "address_line2",
#         "profession", "function", "job_title",
#         "avatar", "photo", "profile_picture",
#     )

#     fields_list: list[str] = []
#     for f in candidates:
#         if _model_has_field(profile.__class__, f) and f not in fields_list:
#             fields_list.append(f)

#     class ProfileUpdateDynamicForm(forms.ModelForm):
#         class Meta:
#             model = profile.__class__
#             fields = tuple(fields_list) if fields_list else tuple()

#     return ProfileUpdateDynamicForm


# # ======================================================
# # Views
# # ======================================================
# @login_required
# def dashboard_profile_view(request):
#     preferred = (request.GET.get("kind") or "").strip().lower()
#     profile, profile_kind = _select_profile(request.user, preferred=preferred)

#     # ✅ IMPORTANT: ne pas bloquer: si pas de profil => page simple + CTA vers edit
#     if not profile:
#         messages.info(request, _("Aucun profil n’est encore renseigné. Vous pouvez le compléter."))
#         return render(
#             request,
#             "dashboard/profile/profile.html",
#             {
#                 "breadcrumbs": breadcrumb(
#                     (_("Dashboard"), safe_reverse("dashboard:hub")),
#                     (_("Profil"), None),
#                 ),
#                 "profile": None,
#                 "profile_kind": "generic",
#                 "profile_status": "",
#                 "profile_phone": "—",
#                 "profile_country": "—",
#                 "profile_city": "—",
#             },
#         )

#     pv = pick_profile_display_values(profile)

#     return render(
#         request,
#         "dashboard/profile/profile.html",
#         {
#             "breadcrumbs": breadcrumb(
#                 (_("Dashboard"), safe_reverse("dashboard:hub")),
#                 (_("Profil"), None),
#             ),
#             "profile": profile,
#             "profile_kind": profile_kind,
#             **pv,
#         },
#     )


# @login_required
# def dashboard_profile_edit_view(request):
#     preferred = (request.GET.get("kind") or "").strip().lower()
#     profile, profile_kind = _select_profile(request.user, preferred=preferred)

#     # ✅ pas de profil => on ne crash pas : on renvoie hub (ou tu peux créer un profil ici si tu veux)
#     if not profile:
#         messages.warning(request, _("Aucun profil n’est associé à ce compte pour le moment."))
#         return redirect("dashboard:hub")

#     UserForm = _build_user_form()
#     user_form = UserForm(request.POST or None, instance=request.user)

#     # 1) si tu as un formulaire custom, on l’utilise
#     try:
#         from dashboard.forms.profile_form import ProfileUpdateForm  # type: ignore
#         ProfileForm = ProfileUpdateForm
#     except Exception:
#         # 2) sinon, fallback dynamique safe
#         ProfileForm = _build_profile_form(profile)

#     profile_form = ProfileForm(
#         request.POST or None,
#         request.FILES or None,
#         instance=profile,
#     )

#     if request.method == "POST":
#         if user_form.is_valid() and profile_form.is_valid():
#             user_form.save()
#             profile_form.save()
#             messages.success(request, _("Profil mis à jour avec succès."))
#             return redirect("dashboard:profile")

#         messages.error(request, _("Veuillez corriger les erreurs du formulaire."))

#     pv = pick_profile_display_values(profile)

#     return render(
#         request,
#         "dashboard/profile/profile_edit.html",
#         {
#             "breadcrumbs": breadcrumb(
#                 (_("Dashboard"), safe_reverse("dashboard:hub")),
#                 (_("Profil"), safe_reverse("dashboard:profile")),
#                 (_("Modifier"), None),
#             ),
#             "profile": profile,
#             "profile_kind": profile_kind,
#             "user_form": user_form,
#             "form": profile_form,
#             "title": _("Modifier le profil"),
#             **pv,
#         },
#     )






# # dashboard/views/dashboard_profile.py
# from __future__ import annotations

# from typing import Any, Optional, Tuple

# from django import forms
# from django.contrib import messages
# from django.contrib.auth import get_user_model
# from django.contrib.auth.decorators import login_required
# from django.core.exceptions import FieldDoesNotExist
# from django.shortcuts import redirect, render
# from django.utils.translation import gettext_lazy as _

# from dashboard.views.utils import breadcrumb, get_user_profile, safe_reverse


# def _model_has_field(model, name: str) -> bool:
#     try:
#         model._meta.get_field(name)
#         return True
#     except FieldDoesNotExist:
#         return False


# def _pick_user_fields(UserModel) -> tuple[str, ...]:
#     candidates = ["first_name", "last_name", "username", "email"]
#     fields = [f for f in candidates if _model_has_field(UserModel, f)]
#     return tuple(fields) if fields else tuple()


# def _build_user_form():
#     UserModel = get_user_model()
#     picked_fields = _pick_user_fields(UserModel)

#     class UserUpdateForm(forms.ModelForm):
#         class Meta:
#             model = UserModel
#             fields = picked_fields

#     return UserUpdateForm


# def _get_profile_any(user, preferred: str = "") -> Tuple[Optional[Any], str]:
#     """
#     Retourne (profile, kind) avec kind in {"economic","social","generic"}.
#     preferred peut venir de ?kind=...
#     """
#     preferred = (preferred or "").strip().lower()
#     if preferred in {"social", "economic", "generic"}:
#         p = get_user_profile(user, preferred=preferred)
#         return p, preferred if p else "generic"

#     # défaut : on prend le profil “principal” (social prioritaire dans utils)
#     p = get_user_profile(user)
#     if not p:
#         return None, "generic"

#     name = p.__class__.__name__.lower()
#     if "economic" in name:
#         return p, "economic"
#     if "social" in name:
#         return p, "social"
#     return p, "generic"


# def _profile_display_values(profile: Any) -> dict:
#     def pick(*names: str) -> Optional[Any]:
#         for n in names:
#             if hasattr(profile, n):
#                 try:
#                     v = getattr(profile, n, None)
#                 except Exception:
#                     v = None
#                 if v not in (None, ""):
#                     return v
#         return None

#     phone = pick("phone_number", "phone")
#     country = pick("country", "country_of_residence")
#     city = pick("city", "city_of_residence")
#     status = pick("status", "validation_status", "account_status")

#     return {
#         "profile_phone": phone or "—",
#         "profile_country": country or "—",
#         "profile_city": city or "—",
#         "profile_status": (str(status).lower().strip() if status else ""),
#     }


# def _build_profile_form(profile: Any):
#     candidates = [
#         "phone_number", "phone",
#         "country", "country_of_residence",
#         "city", "city_of_residence",
#         "address",
#         "profession", "function",
#         "avatar", "photo", "profile_picture",
#     ]

#     fields = []
#     for f in candidates:
#         if _model_has_field(profile.__class__, f) and f not in fields:
#             fields.append(f)

#     fields_tuple = tuple(fields) if fields else ()

#     class ProfileUpdateDynamicForm(forms.ModelForm):
#         class Meta:
#             model = profile.__class__
#             fields = fields_tuple

#     return ProfileUpdateDynamicForm


# @login_required
# def dashboard_profile_view(request):
#     preferred = (request.GET.get("kind") or "").strip().lower()
#     profile, profile_kind = _get_profile_any(request.user, preferred=preferred)

#     if not profile:
#         messages.warning(request, _("Aucun profil n’est associé à ce compte."))
#         return redirect("dashboard:hub")

#     pv = _profile_display_values(profile)

#     return render(
#         request,
#         "dashboard/profile/profile.html",
#         {
#             "breadcrumbs": breadcrumb(
#                 (_("Dashboard"), safe_reverse("dashboard:hub")),
#                 (_("Profil"), None),
#             ),
#             "profile": profile,
#             "profile_kind": profile_kind,
#             **pv,
#         },
#     )


# @login_required
# def dashboard_profile_edit_view(request):
#     preferred = (request.GET.get("kind") or "").strip().lower()
#     profile, profile_kind = _get_profile_any(request.user, preferred=preferred)

#     if not profile:
#         messages.warning(request, _("Aucun profil n’est associé à ce compte."))
#         return redirect("dashboard:hub")

#     UserForm = _build_user_form()
#     user_form = UserForm(request.POST or None, instance=request.user)

#     try:
#         from dashboard.forms.profile_form import ProfileUpdateForm  # type: ignore
#         ProfileForm = ProfileUpdateForm
#     except Exception:
#         ProfileForm = _build_profile_form(profile)

#     profile_form = ProfileForm(
#         request.POST or None,
#         request.FILES or None,
#         instance=profile,
#     )

#     if request.method == "POST":
#         if user_form.is_valid() and profile_form.is_valid():
#             user_form.save()
#             profile_form.save()
#             messages.success(request, _("Profil mis à jour avec succès."))
#             return redirect("dashboard:profile")

#         messages.error(request, _("Veuillez corriger les erreurs du formulaire."))

#     pv = _profile_display_values(profile)

#     return render(
#         request,
#         "dashboard/profile/profile_edit.html",
#         {
#             "breadcrumbs": breadcrumb(
#                 (_("Dashboard"), safe_reverse("dashboard:hub")),
#                 (_("Profil"), safe_reverse("dashboard:profile")),
#                 (_("Modifier"), None),
#             ),
#             "profile": profile,
#             "profile_kind": profile_kind,
#             "user_form": user_form,
#             "form": profile_form,
#             "title": _("Modifier le profil"),
#             **pv,
#         },
#     )





# # dashboard/views/dashboard_profile.py
# from __future__ import annotations

# from typing import Any, Optional, Tuple

# from django import forms
# from django.contrib import messages
# from django.contrib.auth import get_user_model
# from django.contrib.auth.decorators import login_required
# from django.core.exceptions import FieldDoesNotExist
# from django.shortcuts import redirect, render
# from django.utils.translation import gettext_lazy as _

# from dashboard.views.utils import breadcrumb


# # =====================================================
# # Helpers meta (safe)
# # =====================================================
# def _model_has_field(model, name: str) -> bool:
#     try:
#         model._meta.get_field(name)
#         return True
#     except FieldDoesNotExist:
#         return False


# def _pick_user_fields(UserModel) -> tuple[str, ...]:
#     candidates = ["first_name", "last_name", "username", "email"]
#     fields = [f for f in candidates if _model_has_field(UserModel, f)]
#     return tuple(fields) if fields else tuple()


# def _build_user_form():
#     UserModel = get_user_model()
#     picked_fields = _pick_user_fields(UserModel)

#     class UserUpdateForm(forms.ModelForm):
#         class Meta:
#             model = UserModel
#             fields = picked_fields

#     return UserUpdateForm


# def _get_profile_any(user) -> Tuple[Optional[Any], str]:
#     """
#     Retourne (profile, kind) avec kind in {"economic","social","generic"}.
#     On évite de casser si une structure n’existe pas.
#     """
#     # 1) economic profile (DB lookup safe)
#     try:
#         from accounts_users.models.users_economic_profile import UserEconomicProfile  # type: ignore
#         eco = UserEconomicProfile.objects.filter(user=user).first()
#         if eco:
#             return eco, "economic"
#     except Exception:
#         pass

#     # 2) user.profile (related_name="profile")
#     if hasattr(user, "profile") and getattr(user, "profile", None):
#         return user.profile, "generic"

#     # 3) user.social_profile
#     if hasattr(user, "social_profile") and getattr(user, "social_profile", None):
#         return user.social_profile, "social"

#     return None, "generic"


# def _profile_display_values(profile: Any) -> dict:
#     """
#     Pré-calcule les valeurs pour le template :
#     évite {{ profile.phone_number|default:profile.phone }} (qui déclenche failed lookup).
#     """
#     def pick(*names: str) -> Optional[Any]:
#         for n in names:
#             if hasattr(profile, n):
#                 v = getattr(profile, n, None)
#                 if v not in (None, ""):
#                     return v
#         return None

#     phone = pick("phone_number", "phone")
#     country = pick("country", "country_of_residence")
#     city = pick("city", "city_of_residence")
#     status = pick("status", "validation_status")

#     return {
#         "profile_phone": phone or "—",
#         "profile_country": country or "—",
#         "profile_city": city or "—",
#         "profile_status": (str(status).lower() if status else ""),
#     }


# def _build_profile_form(profile: Any):
#     """
#     Form dynamique: ne garde que les champs présents.
#     """
#     candidates = [
#         "phone_number", "phone",
#         "country", "country_of_residence",
#         "city", "city_of_residence",
#         "address", "city_of_residence",
#         "profession", "function",
#         "avatar", "photo", "profile_picture",
#     ]

#     fields = []
#     for f in candidates:
#         if _model_has_field(profile.__class__, f) and f not in fields:
#             fields.append(f)

#     fields_tuple = tuple(fields)

#     class ProfileUpdateDynamicForm(forms.ModelForm):
#         class Meta:
#             model = profile.__class__
#             fields = fields_tuple

#     return ProfileUpdateDynamicForm


# # =====================================================
# # Views
# # =====================================================
# @login_required
# def dashboard_profile_view(request):
#     profile, profile_kind = _get_profile_any(request.user)

#     if not profile:
#         messages.warning(request, _("Aucun profil n’est associé à ce compte."))
#         return redirect("dashboard:hub")

#     pv = _profile_display_values(profile)

#     return render(
#         request,
#         "dashboard/profile/profile.html",
#         {
#             "breadcrumbs": breadcrumb((_("Dashboard"), "/dashboard/"), (_("Profil"), None)),
#             "profile": profile,
#             "profile_kind": profile_kind,
#             **pv,
#         },
#     )


# @login_required
# def dashboard_profile_edit_view(request):
#     profile, profile_kind = _get_profile_any(request.user)
#     if not profile:
#         messages.warning(request, _("Aucun profil n’est associé à ce compte."))
#         return redirect("dashboard:hub")

#     # 1) User form (adaptatif)
#     UserForm = _build_user_form()
#     user_form = UserForm(request.POST or None, instance=request.user)

#     # 2) Profile form (priorité au form existant)
#     try:
#         from dashboard.forms.profile_form import ProfileUpdateForm  # type: ignore
#         ProfileForm = ProfileUpdateForm
#     except Exception:
#         ProfileForm = _build_profile_form(profile)

#     profile_form = ProfileForm(
#         request.POST or None,
#         request.FILES or None,
#         instance=profile,
#     )

#     if request.method == "POST":
#         if user_form.is_valid() and profile_form.is_valid():
#             user_form.save()
#             profile_form.save()
#             messages.success(request, _("Profil mis à jour avec succès."))
#             return redirect("dashboard:profile")

#         messages.error(request, _("Veuillez corriger les erreurs du formulaire."))

#     pv = _profile_display_values(profile)

#     return render(
#         request,
#         "dashboard/profile/profile_edit.html",
#         {
#             "breadcrumbs": breadcrumb(
#                 (_("Dashboard"), "/dashboard/"),
#                 (_("Profil"), "/dashboard/profile/"),
#                 (_("Modifier"), None),
#             ),
#             "profile": profile,
#             "profile_kind": profile_kind,
#             "user_form": user_form,
#             "form": profile_form,
#             "title": _("Modifier le profil"),
#             **pv,
#         },
#     )





# # dashboard/views/dashboard_profile.py
# from __future__ import annotations

# from django import forms
# from django.contrib import messages
# from django.contrib.auth import get_user_model
# from django.contrib.auth.decorators import login_required
# from django.core.exceptions import FieldDoesNotExist
# from django.shortcuts import redirect, render
# from django.utils.translation import gettext_lazy as _

# from dashboard.views.utils import breadcrumb, get_user_profile


# # =====================================================
# # Helpers (prod-safe)
# # =====================================================
# def _model_has_field(model, name: str) -> bool:
#     try:
#         model._meta.get_field(name)
#         return True
#     except FieldDoesNotExist:
#         return False


# def _safe_getattr(obj, name: str, default=None):
#     try:
#         return getattr(obj, name, default)
#     except Exception:
#         return default


# def _pick_value(obj, *attrs: str, default="—"):
#     """
#     Retourne la première valeur non vide trouvée sur obj (attrs),
#     sinon default. Evite les 'Failed lookup...' en template.
#     """
#     for a in attrs:
#         v = _safe_getattr(obj, a, None)
#         if v not in (None, "", [], {}):
#             return v
#     return default


# def _detect_profile_kind(profile) -> str:
#     """
#     Détecte social/economic/generic selon le modèle ou ses attributs.
#     """
#     if not profile:
#         return ""
#     name = (profile.__class__.__name__ or "").lower()
#     if "economic" in name:
#         return "economic"
#     if "social" in name:
#         return "social"

#     # fallback via attributs fréquents
#     if hasattr(profile, "country_of_residence") or hasattr(profile, "profession") or hasattr(profile, "function"):
#         return "economic"
#     if hasattr(profile, "membership_role") or hasattr(profile, "judicial_record"):
#         return "social"
#     return "generic"


# def _detect_profile_status(profile) -> str:
#     """
#     Normalise un statut: approved/pending/rejected/...
#     Compatible avec status, validation_status, is_validated.
#     """
#     if not profile:
#         return ""

#     st = _safe_getattr(profile, "status", "") or _safe_getattr(profile, "validation_status", "") or ""
#     st = (str(st).strip().lower() if st is not None else "")

#     # mappings fréquents
#     if st in ("approved", "active", "validated", "valid", "ok"):
#         return "approved"
#     if st in ("pending", "wait", "waiting", "in_review", "review", "to_validate"):
#         return "pending"
#     if st in ("rejected", "refused", "denied", "blocked"):
#         return "rejected"

#     # fallback is_validated si dispo
#     is_validated = _safe_getattr(profile, "is_validated", None)
#     if is_validated is True:
#         return "approved"
#     if is_validated is False and st:
#         return "pending"

#     return st


# def _pick_user_fields(UserModel) -> tuple[str, ...]:
#     """
#     Sélectionne uniquement des champs existants sur CustomUser
#     pour éviter FieldError.
#     """
#     candidates = ["first_name", "last_name", "full_name", "name", "username", "email"]
#     fields = [f for f in candidates if _model_has_field(UserModel, f)]

#     if not fields:
#         if _model_has_field(UserModel, "email"):
#             return ("email",)
#         if _model_has_field(UserModel, "username"):
#             return ("username",)
#         return tuple()

#     return tuple(fields[:4])


# def _build_user_form():
#     """
#     Construit un ModelForm User de manière dynamique.
#     """
#     UserModel = get_user_model()
#     picked_fields = _pick_user_fields(UserModel)
#     Meta = type("Meta", (), {"model": UserModel, "fields": picked_fields})
#     UserUpdateForm = type("UserUpdateForm", (forms.ModelForm,), {"Meta": Meta})
#     return UserUpdateForm


# def _get_dashboard_profile(user):
#     """
#     Compat:
#     - user.economic_profile (ancienne structure)
#     - user.profile / user.social_profile via helper
#     """
#     econ = _safe_getattr(user, "economic_profile", None)
#     if econ:
#         return econ
#     return get_user_profile(user)


# def _build_profile_form(profile):
#     """
#     Fallback dynamique si ProfileUpdateForm n'existe pas.
#     """
#     fields = []
#     for f in ("phone_number", "phone", "country", "country_of_residence", "address", "city", "city_of_residence", "avatar", "photo", "profile_picture"):
#         if hasattr(profile, f):
#             fields.append(f)

#     Meta = type("Meta", (), {"model": profile.__class__, "fields": tuple(dict.fromkeys(fields))})
#     ProfileUpdateDynamicForm = type("ProfileUpdateDynamicForm", (forms.ModelForm,), {"Meta": Meta})
#     return ProfileUpdateDynamicForm


# # =====================================================
# # Views
# # =====================================================
# @login_required
# def dashboard_profile_view(request):
#     """
#     Affiche le profil, sans faire de lookup fragile dans le template.
#     """
#     profile = _get_dashboard_profile(request.user)

#     if not profile:
#         messages.warning(request, _("Aucun profil associé à ce compte."))
#         return render(
#             request,
#             "dashboard/profile/profile.html",
#             {
#                 "breadcrumbs": breadcrumb((_("Dashboard"), "/dashboard/"), (_("Profil"), None)),
#                 "profile": None,
#                 "profile_kind": "",
#                 "profile_status": "",
#                 "phone_display": "—",
#                 "country_display": "—",
#                 "city_display": "—",
#                 "status_display": "—",
#             },
#         )

#     profile_kind = _detect_profile_kind(profile)
#     profile_status = _detect_profile_status(profile)

#     context = {
#         "breadcrumbs": breadcrumb((_("Dashboard"), "/dashboard/"), (_("Profil"), None)),
#         "profile": profile,
#         "profile_kind": profile_kind,
#         "profile_status": profile_status,

#         # ✅ valeurs sûres pour template
#         "phone_display": _pick_value(profile, "phone_number", "phone", default="—"),
#         "country_display": _pick_value(profile, "country", "country_of_residence", default="—"),
#         "city_display": _pick_value(profile, "city", "city_of_residence", default="—"),
#         "status_display": _pick_value(profile, "status", "validation_status", default=(profile_status or "—")),
#     }

#     return render(request, "dashboard/profile/profile.html", context)


# @login_required
# def dashboard_profile_edit_view(request):
#     """
#     Edition profil (safe):
#     - User form adaptatif (selon champs existants)
#     - Profile form: ProfileUpdateForm si présent, sinon fallback dynamique
#     """
#     profile = _get_dashboard_profile(request.user)
#     if not profile:
#         messages.error(request, _("Aucun profil associé à ce compte."))
#         return redirect("dashboard:router")

#     # 1) User form (adaptatif)
#     UserForm = _build_user_form()
#     user_form = UserForm(request.POST or None, instance=request.user)

#     # 2) Profile form (priorité au form existant)
#     try:
#         from dashboard.forms.profile_form import ProfileUpdateForm  # type: ignore
#         ProfileForm = ProfileUpdateForm
#     except Exception:
#         ProfileForm = _build_profile_form(profile)

#     profile_form = ProfileForm(
#         request.POST or None,
#         request.FILES or None,
#         instance=profile,
#     )

#     if request.method == "POST":
#         if user_form.is_valid() and profile_form.is_valid():
#             user_form.save()
#             profile_form.save()
#             messages.success(request, _("Profil mis à jour avec succès."))
#             return redirect("dashboard:profile")
#         messages.error(request, _("Veuillez corriger les erreurs du formulaire."))

#     return render(
#         request,
#         "dashboard/profile/profile_edit.html",
#         {
#             "breadcrumbs": breadcrumb(
#                 (_("Dashboard"), "/dashboard/"),
#                 (_("Profil"), "/dashboard/profile/"),
#                 (_("Modifier"), None),
#             ),
#             "profile": profile,
#             "user_form": user_form,
#             "form": profile_form,
#             "title": _("Modifier le profil"),
#         },
#     )







# # dashboard/views/dashboard_profile.py
# from __future__ import annotations

# from django import forms
# from django.contrib import messages
# from django.contrib.auth import get_user_model
# from django.contrib.auth.decorators import login_required
# from django.core.exceptions import FieldDoesNotExist
# from django.shortcuts import render, redirect
# from django.utils.translation import gettext_lazy as _

# from dashboard.views.utils import breadcrumb, get_user_profile


# # =====================================================
# # Helpers
# # =====================================================
# def _model_has_field(model, name: str) -> bool:
#     try:
#         model._meta.get_field(name)
#         return True
#     except FieldDoesNotExist:
#         return False
#     except Exception:
#         return False


# def _pick_user_fields(UserModel) -> tuple[str, ...]:
#     """
#     Champs réellement existants sur le modèle User (pas des propriétés).
#     """
#     candidates = ["first_name", "last_name", "username", "email"]
#     fields = [f for f in candidates if _model_has_field(UserModel, f)]
#     return tuple(fields)


# def _build_user_form():
#     UserModel = get_user_model()
#     picked_fields = _pick_user_fields(UserModel)

#     Meta = type("Meta", (), {"model": UserModel, "fields": picked_fields})
#     UserUpdateForm = type("UserUpdateForm", (forms.ModelForm,), {"Meta": Meta})
#     return UserUpdateForm


# def _get_dashboard_profile(user):
#     """
#     Essaie d’être compatible avec tes différentes structures.
#     """
#     # 1) si helper existe et marche (recommandé)
#     try:
#         p = get_user_profile(user)
#         if p:
#             return p
#     except Exception:
#         pass

#     # 2) essais d'attributs courants
#     for attr in ("userprofile", "socialprofile", "economicprofile", "usereconomicprofile", "economic_profile"):
#         try:
#             p = getattr(user, attr, None)
#             if p:
#                 return p
#         except Exception:
#             continue

#     return None


# def _detect_profile_kind(profile) -> str:
#     """
#     Déduit social/economic/generic sans imports risqués.
#     """
#     if not profile:
#         return "generic"

#     name = profile.__class__.__name__.lower()
#     if "economic" in name:
#         return "economic"
#     if "social" in name:
#         return "social"

#     # heuristiques champs
#     if any(hasattr(profile, x) for x in ("country_of_residence", "profession", "function")):
#         return "economic"
#     if any(hasattr(profile, x) for x in ("membership_role", "is_active_member", "judicial_record")):
#         return "social"

#     return "generic"


# def _detect_profile_status(profile) -> str:
#     """
#     Normalise en approved/pending/rejected si possible.
#     """
#     if not profile:
#         return ""
#     raw = (getattr(profile, "status", None) or getattr(profile, "validation_status", None) or "").strip().lower()
#     # normalisations éventuelles
#     if raw in ("approved", "valid", "validated"):
#         return "approved"
#     if raw in ("pending", "wait", "waiting"):
#         return "pending"
#     if raw in ("rejected", "refused", "denied"):
#         return "rejected"
#     return raw


# def _build_profile_form(profile):
#     """
#     ModelForm dynamique uniquement sur les champs existants sur le model.
#     """
#     fields = []
#     candidates = ("phone_number", "phone", "country", "country_of_residence", "city", "city_of_residence", "address", "profile_picture", "avatar", "photo")
#     for f in candidates:
#         if _model_has_field(profile.__class__, f):
#             fields.append(f)

#     Meta = type("Meta", (), {"model": profile.__class__, "fields": tuple(fields)})
#     ProfileUpdateDynamicForm = type("ProfileUpdateDynamicForm", (forms.ModelForm,), {"Meta": Meta})
#     return ProfileUpdateDynamicForm


# def _safe_dashboard_redirect() -> str:
#     # si tu as dashboard:router, garde-le, sinon fallback
#     return "dashboard:router"


# # =====================================================
# # Views
# # =====================================================
# @login_required
# def dashboard_profile_view(request):
#     profile = _get_dashboard_profile(request.user)
#     if not profile:
#         messages.error(request, _("Aucun profil associé à ce compte."))
#         return redirect(_safe_dashboard_redirect())

#     return render(
#         request,
#         "dashboard/profile/profile.html",
#         {
#             "breadcrumbs": breadcrumb((_("Dashboard"), "/dashboard/"), (_("Profil"), None)),
#             "profile": profile,

#             # IMPORTANT: évite “Failed lookup…”
#             "profile_kind": _detect_profile_kind(profile),
#             "profile_status": _detect_profile_status(profile),
#         },
#     )


# @login_required
# def dashboard_profile_edit_view(request):
#     profile = _get_dashboard_profile(request.user)
#     if not profile:
#         messages.error(request, _("Aucun profil associé à ce compte."))
#         return redirect(_safe_dashboard_redirect())

#     # 1) User form
#     UserForm = _build_user_form()
#     user_form = UserForm(request.POST or None, instance=request.user)

#     # 2) Profile form : priorité à ton form si existant
#     try:
#         from dashboard.forms.profile_form import ProfileUpdateForm  # type: ignore
#         ProfileForm = ProfileUpdateForm
#     except Exception:
#         ProfileForm = _build_profile_form(profile)

#     profile_form = ProfileForm(request.POST or None, request.FILES or None, instance=profile)

#     if request.method == "POST":
#         if user_form.is_valid() and profile_form.is_valid():
#             user_form.save()
#             profile_form.save()
#             messages.success(request, _("Profil mis à jour avec succès."))
#             return redirect("dashboard:profile")
#         messages.error(request, _("Veuillez corriger les erreurs du formulaire."))

#     return render(
#         request,
#         "dashboard/profile/profile_edit.html",
#         {
#             "breadcrumbs": breadcrumb(
#                 (_("Dashboard"), "/dashboard/"),
#                 (_("Profil"), "/dashboard/profile/"),
#                 (_("Modifier"), None),
#             ),
#             "profile": profile,
#             "user_form": user_form,
#             "form": profile_form,
#             "title": _("Modifier le profil"),

#             # IMPORTANT
#             "profile_kind": _detect_profile_kind(profile),
#             "profile_status": _detect_profile_status(profile),
#         },
#     )






# # dashboard/views/dashboard_profile.py
# from __future__ import annotations

# from django import forms
# from django.contrib import messages
# from django.contrib.auth import get_user_model
# from django.contrib.auth.decorators import login_required
# from django.core.exceptions import FieldDoesNotExist
# from django.shortcuts import render, redirect
# from django.utils.translation import gettext_lazy as _

# from dashboard.views.utils import breadcrumb, get_user_profile


# # =====================================================
# # Helpers
# # =====================================================
# def _model_has_field(model, name: str) -> bool:
#     try:
#         model._meta.get_field(name)
#         return True
#     except FieldDoesNotExist:
#         return False


# def _pick_user_fields(UserModel) -> tuple[str, ...]:
#     """
#     Sélectionne uniquement des champs existants sur CustomUser
#     pour éviter FieldError.
#     """
#     candidates = ["first_name", "last_name", "full_name", "name", "username", "email"]
#     fields = [f for f in candidates if _model_has_field(UserModel, f)]

#     if not fields:
#         # fallback minimal
#         if _model_has_field(UserModel, "email"):
#             return ("email",)
#         if _model_has_field(UserModel, "username"):
#             return ("username",)
#         return tuple()

#     return tuple(fields[:4])


# def _build_user_form():
#     """
#     Construit un ModelForm User de manière dynamique.
#     """
#     UserModel = get_user_model()
#     picked_fields = _pick_user_fields(UserModel)

#     Meta = type("Meta", (), {"model": UserModel, "fields": picked_fields})
#     UserUpdateForm = type("UserUpdateForm", (forms.ModelForm,), {"Meta": Meta})
#     return UserUpdateForm


# def _get_dashboard_profile(user):
#     """
#     Priorité:
#     1) economic_profile (ancienne structure)
#     2) profile/social_profile via helper
#     """
#     if hasattr(user, "economic_profile") and user.economic_profile:
#         return user.economic_profile
#     return get_user_profile(user)


# def _build_profile_form(profile):
#     """
#     Fallback dynamique si ProfileUpdateForm n'existe pas.
#     """
#     fields = []
#     for f in ("phone_number", "country", "address", "city", "avatar", "photo"):
#         if hasattr(profile, f):
#             fields.append(f)

#     # Si aucun champ, on fabrique un form vide mais valide
#     Meta = type("Meta", (), {"model": profile.__class__, "fields": tuple(fields)})
#     ProfileUpdateDynamicForm = type("ProfileUpdateDynamicForm", (forms.ModelForm,), {"Meta": Meta})
#     return ProfileUpdateDynamicForm


# # =====================================================
# # Views
# # =====================================================
# @login_required
# def dashboard_profile_view(request):
#     profile = _get_dashboard_profile(request.user)
#     if not profile:
#         messages.error(request, _("Aucun profil associé à ce compte."))
#         return redirect("dashboard:router")

#     return render(
#         request,
#         "dashboard/profile/profile.html",
#         {
#             "breadcrumbs": breadcrumb((_("Dashboard"), "/dashboard/"), (_("Profil"), None)),
#             "profile": profile,
#         },
#     )


# @login_required
# def dashboard_profile_edit_view(request):
#     profile = _get_dashboard_profile(request.user)
#     if not profile:
#         messages.error(request, _("Aucun profil associé à ce compte."))
#         return redirect("dashboard:router")

#     # 1) User form (adaptatif)
#     UserForm = _build_user_form()
#     user_form = UserForm(request.POST or None, instance=request.user)

#     # 2) Profile form (priorité au form existant)
#     try:
#         from dashboard.forms.profile_form import ProfileUpdateForm
#         ProfileForm = ProfileUpdateForm
#     except Exception:
#         ProfileForm = _build_profile_form(profile)

#     profile_form = ProfileForm(
#         request.POST or None,
#         request.FILES,
#         instance=profile,
#     )

#     if request.method == "POST":
#         if user_form.is_valid() and profile_form.is_valid():
#             user_form.save()
#             profile_form.save()
#             messages.success(request, _("Profil mis à jour avec succès."))
#             return redirect("dashboard:profile")
#         messages.error(request, _("Veuillez corriger les erreurs du formulaire."))

#     return render(
#         request,
#         "dashboard/profile/profile_edit.html",
#         {
#             "breadcrumbs": breadcrumb(
#                 (_("Dashboard"), "/dashboard/"),
#                 (_("Profil"), "/dashboard/profile/"),
#                 (_("Modifier"), None),
#             ),
#             "profile": profile,
#             "user_form": user_form,
#             "form": profile_form,
#             "title": _("Modifier le profil"),
#         },
#     )




# # dashboard/views/profile.py
# from __future__ import annotations

# from django import forms
# from django.contrib import messages
# from django.contrib.auth import get_user_model
# from django.contrib.auth.decorators import login_required
# from django.core.exceptions import FieldDoesNotExist
# from django.shortcuts import render, redirect
# from django.utils.translation import gettext_lazy as _

# from dashboard.views.utils import breadcrumb, get_user_profile


# # =====================================================
# # Helpers
# # =====================================================
# def _model_has_field(model, name: str) -> bool:
#     try:
#         model._meta.get_field(name)
#         return True
#     except FieldDoesNotExist:
#         return False


# def _pick_user_fields(UserModel) -> tuple[str, ...]:
#     """
#     Sélectionne uniquement des champs existants sur CustomUser
#     pour éviter FieldError.
#     """
#     candidates = ["first_name", "last_name", "full_name", "name", "username", "email"]
#     fields = [f for f in candidates if _model_has_field(UserModel, f)]

#     if not fields:
#         if _model_has_field(UserModel, "email"):
#             return ("email",)
#         if _model_has_field(UserModel, "username"):
#             return ("username",)
#         return tuple()

#     # Limite pour éviter des forms trop longs
#     return tuple(fields[:4])


# def _build_user_form():
#     """
#     Construit un ModelForm User de manière dynamique (Meta dynamique),
#     corrige le problème de scope: class Meta: fields = fields
#     """
#     UserModel = get_user_model()
#     picked_fields = _pick_user_fields(UserModel)

#     Meta = type("Meta", (), {"model": UserModel, "fields": picked_fields})
#     UserUpdateForm = type("UserUpdateForm", (forms.ModelForm,), {"Meta": Meta})
#     return UserUpdateForm


# def _get_dashboard_profile(user):
#     """
#     Priorité:
#     1) economic_profile (ton ancienne structure)
#     2) profile / social_profile via helper
#     """
#     if hasattr(user, "economic_profile") and user.economic_profile:
#         return user.economic_profile
#     return get_user_profile(user)


# def _build_profile_form(profile):
#     """
#     Fallback dynamique si ProfileUpdateForm n'existe pas.
#     """
#     fields = []
#     for f in ("phone_number", "country", "address", "city", "avatar", "photo"):
#         if hasattr(profile, f):
#             fields.append(f)

#     Meta = type("Meta", (), {"model": profile.__class__, "fields": tuple(fields)})
#     ProfileUpdateDynamicForm = type("ProfileUpdateDynamicForm", (forms.ModelForm,), {"Meta": Meta})
#     return ProfileUpdateDynamicForm


# # =====================================================
# # Views
# # =====================================================
# @login_required
# def dashboard_profile_view(request):
#     profile = _get_dashboard_profile(request.user)
#     if not profile:
#         messages.error(request, _("Aucun profil associé à ce compte."))
#         return redirect("dashboard:router")

#     return render(
#         request,
#         "dashboard/profile/profile.html",
#         {
#             "breadcrumbs": breadcrumb((_('Dashboard'), "/dashboard/"), (_("Profil"), None)),
#             "profile": profile,
#         },
#     )


# @login_required
# def dashboard_profile_edit_view(request):
#     profile = _get_dashboard_profile(request.user)
#     if not profile:
#         messages.error(request, _("Aucun profil associé à ce compte."))
#         return redirect("dashboard:router")

#     # 1) User form (adaptatif)
#     UserForm = _build_user_form()
#     user_form = UserForm(request.POST or None, instance=request.user)

#     # 2) Profile form (priorité à ton form existant)
#     try:
#         from dashboard.forms.profile_form import ProfileUpdateForm
#         ProfileForm = ProfileUpdateForm
#     except Exception:
#         ProfileForm = _build_profile_form(profile)

#     profile_form = ProfileForm(
#         request.POST or None,
#         request.FILES or None,
#         instance=profile,
#     )

#     if request.method == "POST":
#         if user_form.is_valid() and profile_form.is_valid():
#             user_form.save()
#             profile_form.save()
#             messages.success(request, _("Profil mis à jour avec succès."))
#             return redirect("dashboard:profile")
#         messages.error(request, _("Veuillez corriger les erreurs du formulaire."))

#     return render(
#         request,
#         "dashboard/profile/profile_edit.html",
#         {
#             "breadcrumbs": breadcrumb(
#                 (_("Dashboard"), "/dashboard/"),
#                 (_("Profil"), "/dashboard/profile/"),
#                 (_("Modifier"), None),
#             ),
#             "profile": profile,
#             "user_form": user_form,  # optionnel dans template
#             "form": profile_form,    # ton template utilise souvent "form"
#             "title": _("Modifier le profil"),
#         },
#     )







# # dashboard/views/profile.py
# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from django.utils.translation import gettext_lazy as _

# from dashboard.forms.profile_form import ProfileUpdateForm


# @login_required
# def dashboard_profile_view(request):
#     """Page d'affichage du profil (économique)."""
#     profile = getattr(request.user, "economic_profile", None)

#     if not profile:
#         messages.error(request, _("Aucun profil associé à ce compte."))
#         return redirect("dashboard:router")  # ✅ existe

#     return render(request, "dashboard/profile/profile.html", {"profile": profile})


# @login_required
# def dashboard_profile_edit_view(request):
#     """Page d'édition du profil (économique)."""
#     profile = getattr(request.user, "economic_profile", None)

#     if not profile:
#         messages.error(request, _("Aucun profil associé à ce compte."))
#         return redirect("dashboard:router")  # ✅ existe

#     if request.method == "POST":
#         form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
#         if form.is_valid():
#             form.save()
#             messages.success(request, _("Profil mis à jour avec succès."))
#             return redirect("dashboard:profile")  # ✅ route profile
#         messages.error(request, _("Veuillez corriger les erreurs du formulaire."))
#     else:
#         form = ProfileUpdateForm(instance=profile)

#     return render(
#         request,
#         "dashboard/profile/profile_edit.html",
#         {"form": form, "profile": profile},
#     )






# # ✅ dashboard/views/profile.py
# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from dashboard.forms.profile_form import ProfileUpdateForm
# from django.utils.translation import gettext_lazy as _


# @login_required
# def dashboard_profile_view(request):
#     """ Page d'affichage du profil """
#     profile = getattr(request.user, "userprofile", None)

#     if not profile:
#         messages.error(request, _("Aucun profil associé à ce compte."))
#         return redirect("dashboard:index")

#     context = {"profile": profile}
#     return render(request, "dashboard/profile/profile.html", context)


# @login_required
# def dashboard_profile_edit_view(request):
#     """ Page d'édition du profil """
#     profile = getattr(request.user, "userprofile", None)

#     if not profile:
#         messages.error(request, _("Aucun profil associé à ce compte."))
#         return redirect("dashboard:index")

#     if request.method == "POST":
#         form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
#         if form.is_valid():
#             form.save()
#             messages.success(request, _("Profil mis à jour avec succès."))
#             return redirect("dashboard:profile")
#         else:
#             messages.error(request, _("Veuillez corriger les erreurs du formulaire."))
#     else:
#         form = ProfileUpdateForm(instance=profile)

#     return render(request, "dashboard/profile/profile_edit.html", {"form": form, "profile": profile})






# # ✅ dashboard/views/profile.py
# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from dashboard.forms.profile_form import ProfileUpdateForm
# from django.utils.translation import gettext_lazy as _

# @login_required
# def dashboard_profile_view(request):
#     profile = getattr(request.user, "userprofile", None)
#     if not profile:
#         messages.error(request, _("Aucun profil associé à ce compte."))
#         return redirect("dashboard:index")  # Ou une vue d’accueil

#     if request.method == "POST":
#         form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
#         if form.is_valid():
#             form.save()
#             messages.success(request, _("Profil mis à jour avec succès."))
#             return redirect("dashboard:profile")
#         else:
#             messages.error(request, _("Veuillez corriger les erreurs du formulaire."))
#     else:
#         form = ProfileUpdateForm(instance=profile)

#     context = {"form": form}
#     return render(request, "dashboard/profile/profile.html", context)



# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render

# @login_required
# def dashboard_profile_view(request):
#     return render(request, "dashboard/profile.html")




