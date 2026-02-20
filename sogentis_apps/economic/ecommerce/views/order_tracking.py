# economic/ecommerce/views/order_tracking.py
from __future__ import annotations

from uuid import UUID

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

try:
    from economic.ecommerce.models import Order  # adapte si ton import est différent
except Exception:  # pragma: no cover
    Order = None  # type: ignore


def _safe_reverse(name: str, **kwargs) -> str:
    try:
        return reverse(name, kwargs=kwargs)
    except Exception:
        return ""


def order_tracking_view(request: HttpRequest) -> HttpResponse:
    """
    ✅ GET : affiche le formulaire (évite HTTP 405)
    ✅ POST : cherche la commande et redirige vers la page détail si possible
    """
    order = None
    query = ""

    # Support GET (?q=...) et POST (tracking_code)
    if request.method == "GET":
        query = (request.GET.get("q") or request.GET.get("uuid") or "").strip()
    elif request.method == "POST":
        query = (request.POST.get("q") or request.POST.get("tracking_code") or request.POST.get("uuid") or "").strip()
    else:
        # Méthodes non supportées
        return render(request, "405.html", status=405)

    if query and Order is not None:
        # 1) tente uuid
        try:
            u = UUID(query)
            try:
                order = Order.objects.filter(uuid=u).first()
            except Exception:
                order = None
        except Exception:
            order = None

        # 2) fallback simple : si ton Order a un champ "number"/"code"/"reference"
        if order is None:
            for field in ("number", "code", "reference", "tracking_code"):
                try:
                    if hasattr(Order, field):
                        order = Order.objects.filter(**{field: query}).first()
                        if order:
                            break
                except Exception:
                    continue

        if request.method == "POST":
            if order:
                url = _safe_reverse("economic:ecommerce:order_detail", uuid=getattr(order, "uuid"))
                if url:
                    return redirect(url)
                messages.success(request, _("Commande trouvée."))
            else:
                messages.error(request, _("Aucune commande trouvée pour ce code."))

    ctx = {
        "tracking_query": query,
        "order": order,
    }
    return render(request, "economic/ecommerce/order_tracking.html", ctx)





# from django.contrib import messages
# from django.shortcuts import redirect
# from django.urls import reverse
# from django.utils.translation import gettext as _
# from django.views.decorators.http import require_POST

# from ..models.order import Order


# @require_POST
# def order_tracking_view(request):
#     uuid = (request.POST.get("uuid") or "").strip()
#     if not uuid:
#         messages.error(request, _("Veuillez saisir un numéro de commande."))
#         return redirect(request.META.get("HTTP_REFERER") or reverse("economic:ecommerce:index"))

#     try:
#         order = Order.objects.get(uuid=uuid)
#     except Order.DoesNotExist:
#         messages.error(request, _("Commande introuvable. Vérifiez le numéro."))
#         return redirect(request.META.get("HTTP_REFERER") or reverse("economic:ecommerce:index"))

#     return redirect("economic:ecommerce:order_detail", uuid=order.uuid)
