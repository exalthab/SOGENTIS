# social/views/payments.py
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from django.urls import reverse
import json
import stripe

from social.models import Donation

# stripe.api_key = settings.STRIPE_SECRET_KEY

# 🔁 Webhook Orange Money
@method_decorator(csrf_exempt, name='dispatch')
class OrangeMoneyWebhookView(View):
    def post(self, request, *args, **kwargs):
        try:
            payload = json.loads(request.body.decode('utf-8'))
            donation_id = payload.get("donation_id")
            if donation_id:
                Donation.objects.filter(id=donation_id).update(status="paid")
        except Exception:
            return HttpResponseBadRequest()
        return JsonResponse({"message": "Webhook Orange Money reçu."}, status=200)

# 🔁 Webhook Stripe
@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(View):
    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', None)
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except (ValueError, stripe.error.SignatureVerificationError):
            return HttpResponseBadRequest()

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            donation_id = session.get('client_reference_id')
            if donation_id:
                Donation.objects.filter(id=donation_id).update(status='paid')
        return HttpResponse(status=200)

# 🔁 Webhook Wave
@method_decorator(csrf_exempt, name='dispatch')
class WaveWebhookView(View):
    def post(self, request, *args, **kwargs):
        # À compléter selon la doc Wave pour valider le paiement
        return HttpResponse("Webhook Wave reçu", status=200)

# 🔁 Webhook PayPal
@method_decorator(csrf_exempt, name='dispatch')
class PayPalWebhookView(View):
    def post(self, request, *args, **kwargs):
        # À compléter selon la doc PayPal pour valider le paiement
        return HttpResponse("Webhook PayPal reçu", status=200)

# 💳 Stripe Checkout (Simulation)
@login_required
def stripe_checkout_view(request, donation_id):
    # ----- Pour production, décommente ce bloc et configure Stripe :
    # donation = get_object_or_404(Donation, id=donation_id)
    # session = stripe.checkout.Session.create(
    #     payment_method_types=['card'],
    #     line_items=[{
    #         'price_data': {
    #             'currency': 'xof',
    #             'unit_amount': int(donation.amount * 100),
    #             'product_data': {
    #                 'name': 'Donation SOGENTIS',
    #             },
    #         },
    #         'quantity': 1,
    #     }],
    #     mode='payment',
    #     success_url=request.build_absolute_uri(reverse('social:donation_success', kwargs={"donation_id": donation_id})),
    #     cancel_url=request.build_absolute_uri(reverse('social:donation_cancel')),
    #     client_reference_id=str(donation.id),
    #     customer_email=donation.email,
    # )
    # return redirect(session.url)

    # ----- Simulation / démo :
    messages.success(request, "Paiement Stripe simulé avec succès.")
    return redirect(reverse("social:donation_success", kwargs={"donation_id": donation_id}))

# 💳 PayPal Checkout
@login_required
def paypal_checkout_view(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id)
    url = f"https://www.paypal.com/checkoutnow?amount={donation.amount}&donation_id={donation.id}"
    return redirect(url)

# 💳 Orange Money Checkout
@login_required
def orange_money_checkout_view(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id)
    url = f"https://om.orange.sn/payment?amount={donation.amount}&ref={donation.id}"
    return redirect(url)

# 💳 Wave Checkout
@login_required
def wave_checkout_view(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id)
    url = f"https://pay.wave.com/sn/pay?amount={donation.amount}&reference={donation.id}"
    return redirect(url)

# 💳 Visa Checkout
@login_required
def visa_checkout_view(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id)
    url = f"https://payment.visa.com/process?amount={donation.amount}&ref={donation.id}"
    return redirect(url)
