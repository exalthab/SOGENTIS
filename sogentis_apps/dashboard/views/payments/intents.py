# dashboard/views/payments/intents.py
from __future__ import annotations

from typing import Any, Dict

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

# Essaie d'importer ton modèle PaymentIntent.
# Adapte le chemin si ton app s'appelle autrement.
try:
    from payments.models import PaymentIntent  # type: ignore
except Exception:  # pragma: no cover
    PaymentIntent = None  # type: ignore


def _can_access(user) -> bool:
    if not user or not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "is_superuser", False) or getattr(user, "is_staff", False):
        return True
    try:
        return bool(
            user.has_perm("payments.view_paymentintent")
            or user.has_perm("dashboard.access_payments_space")
        )
    except Exception:
        return False


def _get_str(request: HttpRequest, key: str, default: str = "") -> str:
    return str(request.GET.get(key, default) or "").strip()


@login_required
def payment_intents_list_view(request: HttpRequest) -> HttpResponse:
    if not _can_access(request.user):
        return render(request, "dashboard/payments/payment_intents_list.html", {"denied": True}, status=403)
    if PaymentIntent is None:
        raise Http404("Payments module not available")

    q = _get_str(request, "q")
    status = _get_str(request, "status")
    provider = _get_str(request, "provider")
    pole = _get_str(request, "pole")
    purpose = _get_str(request, "purpose")

    qs = PaymentIntent.objects.select_related("user").all()

    if status:
        qs = qs.filter(status=status)
    if provider:
        qs = qs.filter(provider=provider)
    if pole:
        qs = qs.filter(pole=pole)
    if purpose:
        qs = qs.filter(purpose=purpose)

    if q:
        qf = Q()
        # champs fréquents (safe)
        if hasattr(PaymentIntent, "reference"):
            qf |= Q(reference__icontains=q)
        if hasattr(PaymentIntent, "provider_ref"):
            qf |= Q(provider_ref__icontains=q)
        if hasattr(PaymentIntent, "provider_payment_id"):
            qf |= Q(provider_payment_id__icontains=q)
        # user email
        qf |= Q(user__email__icontains=q)
        qs = qs.filter(qf)

    qs = qs.order_by("-created_at", "-id")

    paginator = Paginator(qs, 40)
    page_obj = paginator.get_page(_get_str(request, "page", "1"))

    ctx: Dict[str, Any] = {
        "topbar_title": "Payment Intents",
        "topbar_subtitle": "Statuts, provider, pôle, purpose.",
        "intents": page_obj.object_list,
        "page_obj": page_obj,
        "paginator": paginator,
        "q": q,
        "status": status,
        "provider": provider,
        "pole": pole,
        "purpose": purpose,
        # choices (safe)
        "status_choices": getattr(getattr(PaymentIntent, "Status", None), "choices", ()),
        "provider_choices": getattr(getattr(PaymentIntent, "Provider", None), "choices", ()),
        "pole_choices": getattr(getattr(PaymentIntent, "Pole", None), "choices", ()),
        "purpose_choices": getattr(getattr(PaymentIntent, "Purpose", None), "choices", ()),
        "breadcrumbs": [{"label": "Dashboard"}, {"label": "Payments"}, {"label": "Payment Intents"}],
    }
    return render(request, "dashboard/payments/payment_intents_list.html", ctx)


@login_required
def payment_intent_detail_view(request: HttpRequest, uuid) -> HttpResponse:
    if not _can_access(request.user):
        return render(request, "dashboard/payments/payment_intent_detail.html", {"denied": True}, status=403)
    if PaymentIntent is None:
        raise Http404("Payments module not available")

    it = get_object_or_404(PaymentIntent.objects.select_related("user"), uuid=uuid)

    return render(
        request,
        "dashboard/payments/payment_intent_detail.html",
        {
            "topbar_title": "Payment Intent",
            "topbar_subtitle": getattr(it, "reference", None) or str(it.uuid),
            "intent": it,
            "breadcrumbs": [{"label": "Dashboard"}, {"label": "Payments"}, {"label": "Payment Intents"}, {"label": getattr(it, "reference", "")}],
        },
    )






# # dashboard/views/payments/intents.py
# from __future__ import annotations

# from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
# from django.core.paginator import Paginator
# from django.db.models import Q
# from django.shortcuts import get_object_or_404, render

# from payments.models.payment_intent import PaymentIntent

# def staff_required(view_func):
#     return user_passes_test(lambda u: u.is_authenticated and u.is_staff)(view_func)


# @login_required
# @permission_required("payments.view_paymentintent", raise_exception=True)
# def payment_intents_list_view(request):
#     q = (request.GET.get("q") or "").strip()
#     status = (request.GET.get("status") or "").strip()
#     provider = (request.GET.get("provider") or "").strip()
#     pole = (request.GET.get("pole") or "").strip()
#     purpose = (request.GET.get("purpose") or "").strip()

#     qs = PaymentIntent.objects.select_related("user").all()

#     if status:
#         qs = qs.filter(status=status)
#     if provider:
#         qs = qs.filter(provider=provider)
#     if pole:
#         qs = qs.filter(pole=pole)
#     if purpose:
#         qs = qs.filter(purpose=purpose)

#     if q:
#         qs = qs.filter(
#             Q(reference__icontains=q)
#             | Q(provider_ref__icontains=q)
#             | Q(description__icontains=q)
#             | Q(uuid__icontains=q)
#             | Q(user__email__icontains=q)
#         )

#     qs = qs.order_by("-created_at", "-id")

#     paginator = Paginator(qs, 30)
#     page_obj = paginator.get_page(request.GET.get("page") or 1)

#     ctx = {
#         "q": q,
#         "status": status,
#         "provider": provider,
#         "pole": pole,
#         "purpose": purpose,
#         "page_obj": page_obj,
#         "intents": page_obj.object_list,
#         "paginator": paginator,
#         "status_choices": PaymentIntent.Status.choices,
#         "provider_choices": PaymentIntent.Provider.choices,
#         "pole_choices": PaymentIntent.Pole.choices,
#         "purpose_choices": PaymentIntent.Purpose.choices,
#     }
#     return render(request, "dashboard/payments/payment_intents_list.html", ctx)


# @login_required
# @permission_required("payments.view_paymentintent", raise_exception=True)
# def payment_intent_detail_view(request, uuid):
#     intent = get_object_or_404(PaymentIntent.objects.select_related("user"), uuid=uuid)
#     ctx = {"intent": intent}
#     return render(request, "dashboard/payments/payment_intent_detail.html", ctx)
