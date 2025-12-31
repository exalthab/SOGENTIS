# economic/ecommerce/views/switch_mode.py
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme


ALLOWED_MODES = {"B2C", "B2B"}


def switch_mode_view(request, mode):
    # 1) Valider et enregistrer le mode
    if mode in ALLOWED_MODES:
        request.session["commerce_mode"] = mode

    # 2) Redirection vers la page précédente si elle est sûre
    referer = request.META.get("HTTP_REFERER")
    if referer and url_has_allowed_host_and_scheme(
        url=referer,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(referer)

    # 3) Fallback : page e-commerce (index)
    return redirect(reverse("economic:ecommerce:index"))






# # economic/ecommerce/views/switch_mode.py
# from django.shortcuts import redirect
# from django.urls import reverse

# def switch_mode_view(request, mode):
#     if mode in ("B2C", "B2B"):
#         request.session["commerce_mode"] = mode

#     return redirect(request.META.get("HTTP_REFERER", reverse("economic:ecommerce:store")))
