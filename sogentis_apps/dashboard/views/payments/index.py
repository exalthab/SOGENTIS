# dashboard/views/payments/index.py
from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def _can_access_payments(user) -> bool:
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


@login_required
def payments_index_view(request: HttpRequest) -> HttpResponse:
    if not _can_access_payments(request.user):
        return render(
            request,
            "dashboard/payments/index.html",
            {
                "topbar_title": "Payments",
                "topbar_subtitle": "Accès restreint",
                "payments_denied": True,
            },
            status=403,
        )

    return render(
        request,
        "dashboard/payments/index.html",
        {
            "topbar_title": "Payments",
            "topbar_subtitle": "Centre paiements (tous modules).",
            "breadcrumbs": [{"label": "Dashboard"}, {"label": "Payments"}],
        },
    )







# # dashboard/views/payments/index.py
# from __future__ import annotations

# from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
# from django.shortcuts import render

# # -----------------------------
# # Decorator for staff-only views
# # -----------------------------
# def staff_required(view_func):
#     """Require the user to be staff."""
#     return user_passes_test(lambda u: u.is_authenticated and u.is_staff)(view_func)


# # -----------------------------
# # Payments dashboard view
# # -----------------------------
# @login_required
# @permission_required("payments.view_paymentintent", raise_exception=True)
# @staff_required  # optional, if you want only staff to access
# def payments_index_view(request):
#     """
#     Render the payments dashboard.
#     Provides counts, recent PaymentIntents, and context for sidebar.
#     """
#     # -----------------------------
#     # Base context
#     # -----------------------------
#     ctx = {
#         "intents_count": 0,
#         "paid_count": 0,
#         "pending_count": 0,
#         "recent": [],
#     }

#     # -----------------------------
#     # Resolver match for sidebar active links
#     # -----------------------------
#     rm = getattr(request, "resolver_match", None)
#     ctx["uname"] = getattr(rm, "url_name", "") if rm else ""
#     ctx["nss"] = getattr(rm, "namespaces", ()) if rm else ()

#     # -----------------------------
#     # PaymentIntent stats
#     # -----------------------------
#     try:
#         from payments.models import PaymentIntent  # type: ignore

#         ctx["intents_count"] = PaymentIntent.objects.count()
#         ctx["paid_count"] = PaymentIntent.objects.filter(
#             status=getattr(PaymentIntent.Status, "PAID", "PAID")
#         ).count()
#         ctx["pending_count"] = PaymentIntent.objects.filter(
#             status=getattr(PaymentIntent.Status, "PENDING", "PENDING")
#         ).count()
#         ctx["recent"] = PaymentIntent.objects.select_related("user").order_by(
#             "-created_at", "-id"
#         )[:12]

#     except Exception:
#         # Fail silently if PaymentIntent is missing
#         pass

#     return render(request, "dashboard/payments/index.html", ctx)






# # dashboard/views/payments/index.py
# from __future__ import annotations

# from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
# from django.shortcuts import render

# def staff_required(view_func):
#     return user_passes_test(lambda u: u.is_authenticated and u.is_staff)(view_func)


# @login_required
# @permission_required("payments.view_paymentintent", raise_exception=True)
# def payments_index_view(request):
#     ctx = {"intents_count": 0, "paid_count": 0, "pending_count": 0, "recent": []}
#     try:
#         from payments.models import PaymentIntent  # type: ignore

#         ctx["intents_count"] = PaymentIntent.objects.count()
#         ctx["paid_count"] = PaymentIntent.objects.filter(status=getattr(PaymentIntent.Status, "PAID", "PAID")).count()
#         ctx["pending_count"] = PaymentIntent.objects.filter(status=getattr(PaymentIntent.Status, "PENDING", "PENDING")).count()
#         ctx["recent"] = PaymentIntent.objects.select_related("user").order_by("-created_at", "-id")[:12]
#     except Exception:
#         pass
#     return render(request, "dashboard/payments/index.html", ctx)