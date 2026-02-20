# payments/views/providers.py
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext_lazy as _

from payments.models import PaymentIntent


@login_required
def provider_start_view(request, uuid, provider: str):
    intent = get_object_or_404(PaymentIntent, uuid=uuid)

    if intent.user_id != request.user.id and not request.user.is_staff:
        raise Http404()

    provider = (provider or "").lower().strip()
    if provider not in {p for p, _ in PaymentIntent.Provider.choices}:
        messages.error(request, _("Moyen de paiement invalide."))
        return redirect("payments:checkout", uuid=intent.uuid)

    # ✅ ici tu branches tes intégrations réelles
    # - créer session/checkout provider
    # - set provider_ref
    # - redirect provider_url

    intent.mark_pending(provider=provider, provider_ref="")
    messages.info(request, _("Redirection vers le paiement %(p)s…") % {"p": provider})

    # TODO: remplacer par l'URL provider réelle
    return redirect("payments:checkout", uuid=intent.uuid)
