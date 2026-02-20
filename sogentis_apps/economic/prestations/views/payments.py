# economic/prestations/views/payments.py
from __future__ import annotations

from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from payments.services.intent_service import create_intent

from ..models import PackageOffer, Prestation, PrestationEntitlement, PrestationPackage, PrestationPlan
from ..models.entitlements import EntitlementStatus


def _pick_price(obj) -> Decimal | None:
    for attr in ("display_price", "min_price", "price", "base_price", "total_price"):
        val = getattr(obj, attr, None)
        if val is None or str(val) == "":
            continue
        try:
            d = Decimal(val)
            if d > 0:
                return d
        except Exception:
            continue
    return None


def _cur(request: HttpRequest) -> str:
    return (request.session.get("ECOMMERCE_CURRENCY") or "XOF").upper()


def _abs(request: HttpRequest, url_name: str, **kwargs) -> str:
    return request.build_absolute_uri(reverse(url_name, kwargs=kwargs))


def _intent_session_key(kind: str, obj_id: int, amount: Decimal, currency: str) -> str:
    return f"pay:intent:{kind}:{obj_id}:{currency}:{str(amount)}"


def _active_entitlement_exists(*, user, plan=None, offer=None) -> bool:
    try:
        qs = PrestationEntitlement.objects.filter(user=user, status=EntitlementStatus.ACTIVE)
        if plan is not None:
            qs = qs.filter(prestation_plan=plan)
        if offer is not None:
            qs = qs.filter(package_offer=offer)
        return qs.exists()
    except Exception:
        return False


@login_required
def pay_prestation_start_view(request: HttpRequest, slug: str):
    """
    /economic/prestations/<slug>/pay/?offer=<plan_slug>
    - Compte requis
    - Si plan choisi => paye PrestationPlan (recommandé)
    - Sinon fallback sur Prestation
    - Si déjà entitlement actif => redirection mes téléchargements
    """
    prestation = get_object_or_404(Prestation, slug=slug, is_active=True)
    currency = _cur(request)

    offer_slug = (request.GET.get("offer") or request.POST.get("offer") or "").strip()
    force_new = (request.GET.get("new") or "").strip() == "1"

    # --- Prefer: pay a specific plan (offer)
    if offer_slug:
        plan = get_object_or_404(
            PrestationPlan.objects.select_related("prestation").filter(is_active=True, prestation__is_active=True),
            prestation=prestation,
            slug=offer_slug,
        )

        if plan.price is None:
            messages.info(request, _("Cette offre est sur devis."))
            return redirect("economic:prestations:quote", slug=prestation.slug)

        if not getattr(plan, "allow_online_payment", False):
            messages.info(request, _("Paiement en ligne indisponible pour cette offre."))
            return redirect("economic:prestations:quote", slug=prestation.slug)

        if _active_entitlement_exists(user=request.user, plan=plan):
            messages.success(request, _("Vous avez déjà accès à cette offre."))
            return redirect("economic:prestations:my_downloads")

        amount = _pick_price(plan) or Decimal(plan.price)

        # anti-doublon (session)
        s_key = _intent_session_key("prestation_plan", int(plan.pk), amount, currency)
        if not force_new:
            existing = (request.session.get(s_key) or "").strip()
            if existing:
                return redirect("payments:checkout", uuid=existing)

        intent = create_intent(
            user=request.user,
            amount=amount,
            currency=currency,
            pole="ECONOMIC",
            description=_("Paiement offre prestation : %(t)s") % {"t": getattr(plan, "title", "") or plan.slug},
            obj=plan,
            metadata={
                "kind": "prestation_plan",
                "prestation_slug": prestation.slug,
                "plan_slug": plan.slug,
                "plan_id": int(plan.pk),
            },
            return_url=_abs(request, "economic:prestations:my_downloads"),
            cancel_url=_abs(request, "economic:prestations:prestation_offer_detail", slug=prestation.slug, offer_slug=plan.slug),
        )
        request.session[s_key] = str(intent.uuid)
        request.session.modified = True
        return redirect("payments:checkout", uuid=intent.uuid)

    # --- Fallback: pay base prestation
    price = _pick_price(prestation)
    if not price:
        messages.info(request, _("Cette prestation est sur devis."))
        return redirect("economic:prestations:quote", slug=prestation.slug)

    s_key = _intent_session_key("prestation", int(prestation.pk), price, currency)
    if not force_new:
        existing = (request.session.get(s_key) or "").strip()
        if existing:
            return redirect("payments:checkout", uuid=existing)

    intent = create_intent(
        user=request.user,
        amount=price,
        currency=currency,
        pole="ECONOMIC",
        description=_("Paiement prestation : %(t)s") % {"t": getattr(prestation, "title", "") or prestation.slug},
        obj=prestation,
        metadata={"kind": "prestation", "slug": prestation.slug, "prestation_id": int(prestation.pk)},
        return_url=_abs(request, "economic:prestations:detail", slug=prestation.slug),
        cancel_url=_abs(request, "economic:prestations:detail", slug=prestation.slug),
    )
    request.session[s_key] = str(intent.uuid)
    request.session.modified = True
    return redirect("payments:checkout", uuid=intent.uuid)


@login_required
def pay_package_start_view(request: HttpRequest, slug: str):
    """
    /economic/prestations/packs/<slug>/pay/?offer=<offer_slug>
    - Compte requis
    - Si offer choisi => paye PackageOffer (recommandé)
    - Sinon fallback sur Package
    - Si déjà entitlement actif => redirection mes téléchargements
    """
    package = get_object_or_404(PrestationPackage, slug=slug, is_active=True)
    currency = _cur(request)

    offer_slug = (request.GET.get("offer") or request.POST.get("offer") or "").strip()
    force_new = (request.GET.get("new") or "").strip() == "1"

    # --- Prefer: pay a specific offer
    if offer_slug:
        offer = get_object_or_404(
            PackageOffer.objects.select_related("package").filter(is_active=True, package__is_active=True),
            package=package,
            slug=offer_slug,
        )

        if offer.price is None:
            messages.info(request, _("Cette offre est sur devis."))
            return redirect("economic:prestations:package_quote", slug=package.slug)

        if not getattr(offer, "allow_online_payment", False):
            messages.info(request, _("Paiement en ligne indisponible pour cette offre."))
            return redirect("economic:prestations:package_quote", slug=package.slug)

        if _active_entitlement_exists(user=request.user, offer=offer):
            messages.success(request, _("Vous avez déjà accès à cette offre."))
            return redirect("economic:prestations:my_downloads")

        amount = _pick_price(offer) or Decimal(offer.price)

        s_key = _intent_session_key("package_offer", int(offer.pk), amount, currency)
        if not force_new:
            existing = (request.session.get(s_key) or "").strip()
            if existing:
                return redirect("payments:checkout", uuid=existing)

        intent = create_intent(
            user=request.user,
            amount=amount,
            currency=currency,
            pole="ECONOMIC",
            description=_("Paiement offre pack : %(t)s") % {"t": getattr(offer, "title", "") or offer.slug},
            obj=offer,
            metadata={
                "kind": "package_offer",
                "package_slug": package.slug,
                "offer_slug": offer.slug,
                "offer_id": int(offer.pk),
            },
            return_url=_abs(request, "economic:prestations:my_downloads"),
            cancel_url=_abs(request, "economic:prestations:package_offer_detail", slug=package.slug, offer_slug=offer.slug),
        )
        request.session[s_key] = str(intent.uuid)
        request.session.modified = True
        return redirect("payments:checkout", uuid=intent.uuid)

    # --- Fallback: pay base package
    price = _pick_price(package)
    if not price:
        messages.info(request, _("Ce pack est sur devis."))
        return redirect("economic:prestations:package_quote", slug=package.slug)

    s_key = _intent_session_key("package", int(package.pk), price, currency)
    if not force_new:
        existing = (request.session.get(s_key) or "").strip()
        if existing:
            return redirect("payments:checkout", uuid=existing)

    intent = create_intent(
        user=request.user,
        amount=price,
        currency=currency,
        pole="ECONOMIC",
        description=_("Paiement pack : %(t)s") % {"t": getattr(package, "title", "") or package.slug},
        obj=package,
        metadata={"kind": "package", "slug": package.slug, "package_id": int(package.pk)},
        return_url=_abs(request, "economic:prestations:package_detail", slug=package.slug),
        cancel_url=_abs(request, "economic:prestations:package_detail", slug=package.slug),
    )
    request.session[s_key] = str(intent.uuid)
    request.session.modified = True
    return redirect("payments:checkout", uuid=intent.uuid)






# # economic/prestations/views/payments.py
# from __future__ import annotations

# from decimal import Decimal

# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import get_object_or_404, redirect
# from django.utils.translation import gettext_lazy as _

# from payments.services.intent_service import create_intent
# from ..models import Prestation, PrestationPackage


# def _pick_price(obj) -> Decimal | None:
#     for attr in ("display_price", "min_price", "price", "base_price", "total_price"):
#         val = getattr(obj, attr, None)
#         if val is not None and str(val) != "":
#             try:
#                 d = Decimal(val)
#                 if d > 0:
#                     return d
#             except Exception:
#                 continue
#     return None


# @login_required
# def pay_prestation_start_view(request, slug: str):
#     prestation = get_object_or_404(Prestation, slug=slug, is_active=True)

#     price = _pick_price(prestation)
#     if not price:
#         messages.info(request, _("Cette prestation est sur devis."))
#         return redirect("economic:prestations:quote", slug=prestation.slug)

#     currency = (request.session.get("ECOMMERCE_CURRENCY") or "XOF").upper()

#     intent = create_intent(
#         user=request.user,
#         amount=price,
#         currency=currency,
#         pole="ECONOMIC",
#         description=_("Paiement prestation : %(t)s") % {"t": getattr(prestation, "title", "") or prestation.slug},
#         obj=prestation,
#         metadata={"kind": "prestation", "slug": prestation.slug},
#         return_url=redirect("economic:prestations:detail", slug=prestation.slug).url,
#         cancel_url=redirect("economic:prestations:detail", slug=prestation.slug).url,
#     )
#     return redirect("payments:checkout", uuid=intent.uuid)


# @login_required
# def pay_package_start_view(request, slug: str):
#     package = get_object_or_404(PrestationPackage, slug=slug, is_active=True)

#     price = _pick_price(package)
#     if not price:
#         messages.info(request, _("Ce pack est sur devis."))
#         return redirect("economic:prestations:package_quote", slug=package.slug)

#     currency = (request.session.get("ECOMMERCE_CURRENCY") or "XOF").upper()

#     intent = create_intent(
#         user=request.user,
#         amount=price,
#         currency=currency,
#         pole="ECONOMIC",
#         description=_("Paiement pack : %(t)s") % {"t": getattr(package, "title", "") or package.slug},
#         obj=package,
#         metadata={"kind": "package", "slug": package.slug},
#         return_url=redirect("economic:prestations:package_detail", slug=package.slug).url,
#         cancel_url=redirect("economic:prestations:package_detail", slug=package.slug).url,
#     )
#     return redirect("payments:checkout", uuid=intent.uuid)

