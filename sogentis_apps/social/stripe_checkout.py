import stripe
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(request):
    if request.method == "POST":
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "xof",
                            "unit_amount": int(
                                float(request.POST.get("amount", 0)) * 100
                            ),
                            "product_data": {
                                "name": f"Don de {request.POST.get('full_name', 'Bienfaiteur')}",
                            },
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url=request.build_absolute_uri(
                    reverse("social:donation_success")
                ),
                cancel_url=request.build_absolute_uri(reverse("social:donation")),
                metadata={
                    "full_name": request.POST.get("full_name"),
                    "email": request.POST.get("email"),
                    "message": request.POST.get("message", ""),
                },
            )
            return redirect(checkout_session.url)
        except Exception as e:
            return JsonResponse({"error": str(e)})

    return HttpResponse(status=400)