# economic/ecommerce/views/mode.py
from django.shortcuts import redirect

def switch_commerce_mode(request, mode):
    if mode in ["B2C", "B2B"]:
        request.session["commerce_mode"] = mode
    return redirect(request.META.get("HTTP_REFERER", "/"))
