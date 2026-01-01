# economic/ecommerce/views/mode.py

from django.shortcuts import render


def ecommerce_mode_info_view(request):
    """
    Page d’info sur les modes B2C / B2B.
    Template à créer si utile : economic/ecommerce/mode.html
    """
    current_mode = request.session.get("commerce_mode", "B2C")
    context = {
        "commerce_mode": current_mode,
    }
    return render(request, "economic/ecommerce/mode.html", context)




# # economic/ecommerce/views/mode.py
# from django.shortcuts import redirect

# def switch_commerce_mode(request, mode):
#     if mode in ["B2C", "B2B"]:
#         request.session["commerce_mode"] = mode
#     return redirect(request.META.get("HTTP_REFERER", "/"))
