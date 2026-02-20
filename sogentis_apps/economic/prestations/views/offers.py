# economic/prestations/views/offers.py
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from ..models import PackageOffer, PrestationEntitlement, PrestationPlan
from ..models.entitlements import EntitlementStatus


def _cur(request: HttpRequest) -> str:
    return (request.session.get("ECOMMERCE_CURRENCY") or "XOF").upper()


def _active_entitlement_for_plan(user, plan: PrestationPlan) -> PrestationEntitlement | None:
    try:
        return (
            PrestationEntitlement.objects.filter(
                user=user,
                status=EntitlementStatus.ACTIVE,
                prestation_plan=plan,
            )
            .order_by("-created_at", "-id")
            .first()
        )
    except Exception:
        return None


def _active_entitlement_for_offer(user, offer: PackageOffer) -> PrestationEntitlement | None:
    try:
        return (
            PrestationEntitlement.objects.filter(
                user=user,
                status=EntitlementStatus.ACTIVE,
                package_offer=offer,
            )
            .order_by("-created_at", "-id")
            .first()
        )
    except Exception:
        return None


@login_required
def prestation_offer_detail_view(request: HttpRequest, slug: str, offer_slug: str) -> HttpResponse:
    """
    /economic/prestations/<slug>/offers/<offer_slug>/
    Page option/plan d'une prestation.
    - Compte requis (login_required)
    - Affiche "déjà acquis" si entitlement actif
    """
    plan = get_object_or_404(
        PrestationPlan.objects.select_related("prestation").filter(is_active=True, prestation__is_active=True),
        prestation__slug=slug,
        slug=offer_slug,
    )

    ent = _active_entitlement_for_plan(request.user, plan)
    has_access = bool(ent)

    can_pay = bool(plan.allow_online_payment and plan.price is not None and not has_access)
    is_quote_only = plan.price is None

    download_url = None
    if ent and getattr(ent, "download_token", None):
        try:
            download_url = redirect("economic:prestations:download", token=ent.download_token).url
        except Exception:
            download_url = None

    return render(
        request,
        "economic/prestations/offers/prestation_offer_detail.html",
        {
            "cur": _cur(request),
            "prestation": plan.prestation,
            "plan": plan,
            "offer": plan,

            "has_access": has_access,
            "entitlement": ent,
            "download_url": download_url,

            "can_pay": can_pay,
            "is_quote_only": is_quote_only,
        },
    )


@login_required
def package_offer_detail_view(request: HttpRequest, slug: str, offer_slug: str) -> HttpResponse:
    """
    /economic/prestations/packs/<slug>/offers/<offer_slug>/
    Page option/offre d'un pack.
    - Compte requis
    - Affiche "déjà acquis" si entitlement actif
    """
    offer = get_object_or_404(
        PackageOffer.objects.select_related("package").filter(is_active=True, package__is_active=True),
        package__slug=slug,
        slug=offer_slug,
    )

    ent = _active_entitlement_for_offer(request.user, offer)
    has_access = bool(ent)

    can_pay = bool(offer.allow_online_payment and offer.price is not None and not has_access)
    is_quote_only = offer.price is None

    download_url = None
    if ent and getattr(ent, "download_token", None):
        try:
            download_url = redirect("economic:prestations:download", token=ent.download_token).url
        except Exception:
            download_url = None

    return render(
        request,
        "economic/prestations/offers/package_offer_detail.html",
        {
            "cur": _cur(request),
            "package": offer.package,
            "offer": offer,

            "has_access": has_access,
            "entitlement": ent,
            "download_url": download_url,

            "can_pay": can_pay,
            "is_quote_only": is_quote_only,
        },
    )


@login_required
def entitlement_download_view(request: HttpRequest, token: str) -> HttpResponse:
    """
    /economic/prestations/download/<uuid:token>/
    Téléchargement sécurisé :
    - user = request.user
    - entitlement ACTIVE
    - limite / expiration gérée par ent.can_download()
    """
    ent = get_object_or_404(
        PrestationEntitlement.objects.select_related("user").filter(
            user=request.user,
            download_token=token,
            status=EntitlementStatus.ACTIVE,
        ),
    )

    if not ent.can_download():
        messages.error(request, _("Lien indisponible (expiré ou limite atteinte)."))
        return redirect("economic:prestations:my_downloads")

    f = getattr(ent, "deliverable_file", None)
    if not f:
        url = getattr(ent, "deliverable_url", "") or ""
        if url:
            try:
                ent.mark_download()  # compte aussi les accès via URL
            except Exception:
                pass
            return redirect(url)
        raise Http404("No deliverable")

    try:
        ent.mark_download()
        filename = (getattr(f, "name", "") or "").split("/")[-1] or "download"
        return FileResponse(f.open("rb"), as_attachment=True, filename=filename)
    except Exception:
        raise Http404("Download error")


@login_required
def my_entitlements_view(request: HttpRequest) -> HttpResponse:
    """
    /economic/prestations/my-downloads/
    Liste des accès digitaux de l'utilisateur.
    """
    qs = (
        PrestationEntitlement.objects.filter(user=request.user)
        .select_related("prestation_plan", "package_offer")
        .order_by("-created_at", "-id")
    )

    return render(
        request,
        "economic/prestations/offers/my_entitlements.html",
        {"cur": _cur(request), "entitlements": qs},
    )





# # economic/prestations/views/offers.py
# from __future__ import annotations

# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.http import FileResponse, Http404, HttpRequest, HttpResponse
# from django.shortcuts import get_object_or_404, redirect, render
# from django.utils.translation import gettext_lazy as _

# from ..models import PackageOffer, PrestationEntitlement, PrestationPlan
# from ..models.entitlements import EntitlementStatus


# def _cur(request: HttpRequest) -> str:
#     return (request.session.get("ECOMMERCE_CURRENCY") or "XOF").upper()


# @login_required
# def prestation_offer_detail_view(request: HttpRequest, slug: str, offer_slug: str) -> HttpResponse:
#     """
#     /economic/prestations/<slug>/offers/<offer_slug>/
#     Page option/plan (Infomaniak-like) d'une prestation.
#     """
#     plan = get_object_or_404(
#         PrestationPlan.objects.select_related("prestation").filter(is_active=True, prestation__is_active=True),
#         prestation__slug=slug,
#         slug=offer_slug,
#     )

#     return render(
#         request,
#         "economic/prestations/offers/prestation_offer_detail.html",
#         {
#             "cur": _cur(request),
#             "prestation": plan.prestation,
#             "plan": plan,
#             "offer": plan,
#             "can_pay": bool(plan.allow_online_payment and plan.price is not None),
#             "is_quote_only": plan.price is None,
#         },
#     )


# @login_required
# def package_offer_detail_view(request: HttpRequest, slug: str, offer_slug: str) -> HttpResponse:
#     """
#     /economic/prestations/packs/<slug>/offers/<offer_slug>/
#     Page option/offre d'un pack.
#     """
#     offer = get_object_or_404(
#         PackageOffer.objects.select_related("package").filter(is_active=True, package__is_active=True),
#         package__slug=slug,
#         slug=offer_slug,
#     )

#     return render(
#         request,
#         "economic/prestations/offers/package_offer_detail.html",
#         {
#             "cur": _cur(request),
#             "package": offer.package,
#             "offer": offer,
#             "can_pay": bool(offer.allow_online_payment and offer.price is not None),
#             "is_quote_only": offer.price is None,
#         },
#     )


# @login_required
# def entitlement_download_view(request: HttpRequest, token: str) -> HttpResponse:
#     """
#     /economic/prestations/download/<uuid>/
#     Téléchargement sécurisé (dashboard / lien privé).
#     """
#     ent = get_object_or_404(
#         PrestationEntitlement.objects.select_related("user", "prestation_plan", "package_offer").filter(
#             user=request.user,
#             download_token=token,
#             status=EntitlementStatus.ACTIVE,
#         ),
#     )

#     if not ent.can_download():
#         messages.error(request, _("Lien indisponible (expiré ou limite atteinte)."))
#         return redirect("dashboard:hub")

#     f = ent.deliverable_file
#     if not f:
#         url = ent.deliverable_url
#         if url:
#             return redirect(url)
#         raise Http404("No deliverable")

#     try:
#         ent.mark_download()
#         return FileResponse(f.open("rb"), as_attachment=True, filename=f.name.split("/")[-1])
#     except Exception as exc:
#         raise Http404(str(exc))


# @login_required
# def my_entitlements_view(request: HttpRequest) -> HttpResponse:
#     """
#     /economic/prestations/my-downloads/
#     Liste des accès digitaux de l'utilisateur.
#     """
#     qs = (
#         PrestationEntitlement.objects.filter(user=request.user)
#         .select_related("prestation_plan", "package_offer", "prestation", "package")
#         .order_by("-created_at", "-id")
#     )

#     return render(
#         request,
#         "economic/prestations/offers/my_entitlements.html",
#         {
#             "cur": _cur(request),
#             "entitlements": qs,
#         },
#     )
