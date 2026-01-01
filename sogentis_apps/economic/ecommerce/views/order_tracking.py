from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from ..models.order import Order


@require_POST
def order_tracking_view(request):
    uuid = (request.POST.get("uuid") or "").strip()
    if not uuid:
        messages.error(request, _("Veuillez saisir un numéro de commande."))
        return redirect(request.META.get("HTTP_REFERER") or reverse("economic:ecommerce:index"))

    try:
        order = Order.objects.get(uuid=uuid)
    except Order.DoesNotExist:
        messages.error(request, _("Commande introuvable. Vérifiez le numéro."))
        return redirect(request.META.get("HTTP_REFERER") or reverse("economic:ecommerce:index"))

    return redirect("economic:ecommerce:order_detail", uuid=order.uuid)
