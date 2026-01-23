# economic/services/views/package_quote.py
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from ..models import ServicePackage
from ..models.service_request import ServiceRequest
from ..forms import QuoteRequestForm


@login_required
def package_quote_view(request, slug):
    """
    Page /economic/services/packs/<slug>/quote/
    - Demande de devis pour un pack précis.
    - On réutilise QuoteRequestForm (comme request_quote_view).
    - On enregistre en ServiceRequest (logique actuelle du module).
    """

    package = get_object_or_404(ServicePackage, slug=slug, is_active=True)

    if request.method == "POST":
        form = QuoteRequestForm(request.POST)
        if form.is_valid():
            sr: ServiceRequest = form.save(commit=False)
            sr.user = request.user

            # ---------------------------------------------------------
            # ✅ Intégration "ce qui manque" :
            # Si ServiceRequest.service est obligatoire (souvent le cas),
            # on rattache un service "principal" du pack (le 1er).
            # ---------------------------------------------------------
            first_service = package.services.first()

            # On tente d'affecter service uniquement si l'attribut existe
            # (selon ton modèle ServiceRequest)
            if hasattr(sr, "service"):
                if first_service:
                    sr.service = first_service

            # ---------------------------------------------------------
            # Enrichir le message avec info pack + liste services
            # (sans casser le texte utilisateur)
            # ---------------------------------------------------------
            pack_name = package.safe_translation_getter("name", any_language=True) or package.slug
            extra_lines = [
                _("Demande de devis — Pack : %(pack)s") % {"pack": pack_name},
            ]

            services = list(package.services.all())
            if services:
                extra_lines.append(_("Services inclus :"))
                for s in services[:20]:
                    title = s.safe_translation_getter("title", any_language=True) or s.slug
                    extra_lines.append(f"- {title}")
                if len(services) > 20:
                    extra_lines.append(_("… et %(n)s autres") % {"n": len(services) - 20})

            extra = "\n".join(extra_lines).strip()

            base_msg = (getattr(sr, "message", "") or "").strip()
            sr.message = (base_msg + "\n\n" + extra).strip() if base_msg else extra

            sr.save()

            messages.success(request, _("Votre demande de devis a été envoyée."))
            return redirect("economic:services:package_detail", slug=package.slug)
    else:
        form = QuoteRequestForm()

    return render(
        request,
        "economic/services/package_quote_form.html",
        {
            "package": package,
            "form": form,
        },
    )





# # economic/services/views/package_quote.py
# from __future__ import annotations

# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import get_object_or_404, redirect, render
# from django.utils.translation import gettext_lazy as _

# from ..models import ServicePackage
# from ..models.service_request import ServiceRequest
# from ..forms import QuoteRequestForm


# @login_required
# def package_quote_view(request, slug):
#     package = get_object_or_404(ServicePackage, slug=slug, is_active=True)

#     if request.method == "POST":
#         form = QuoteRequestForm(request.POST)
#         if form.is_valid():
#             sr: ServiceRequest = form.save(commit=False)
#             sr.user = request.user

#             # ✅ pack -> on tente d’attacher un service si ton modèle l’exige
#             if hasattr(sr, "service_id"):
#                 first_service = package.services.first()
#                 if first_service:
#                     sr.service = first_service

#             # enrichir le message automatiquement
#             base_msg = (getattr(sr, "message", "") or "").strip()
#             extra = _("Demande de devis pour le pack : ") + (package.safe_translation_getter("name", any_language=True) or package.slug)
#             sr.message = (base_msg + "\n\n" + extra).strip() if base_msg else extra

#             sr.save()
#             messages.success(request, _("Votre demande de devis a été envoyée."))
#             return redirect("economic:services:package_detail", slug=package.slug)
#     else:
#         form = QuoteRequestForm()

#     return render(
#         request,
#         "economic/services/package_quote_form.html",
#         {"package": package, "form": form},
#     )
