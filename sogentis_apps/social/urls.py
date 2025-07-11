#social/urls.py
from django.urls import path

from social.views.publication_view import (
    publication_list,
    publication_request_access,
    publication_pay_and_request,
    download_publication,
    publication_email_request,
)
from social.views.donations import (
    soci_index,
    donation_view,
    public_donations_view,
    donation_success_view,
    donation_cancel_view,
    download_receipt_view,
    donation_payment_choice_view,
    donation_history_view,
)
from social.views.publication_view import publication_list
from social.views.projects import (
    projects_list_view,
    create_project_view,
    update_project_view,
    delete_project_view,
    project_detail_view,
)
from social.views.payments import (
    stripe_checkout_view,
    paypal_checkout_view,
    orange_money_checkout_view,
    wave_checkout_view,
    visa_checkout_view,
    PayPalWebhookView,
    WaveWebhookView,
    OrangeMoneyWebhookView,
    StripeWebhookView,
)
from social.views.volunteers import engagement_view
from social.search_view import search_view

app_name = "social"

urlpatterns = [
    # 🌍 Accueil et recherche
    path("", soci_index, name="index"),
    path("search/", search_view, name="search"),

    # 💕 Dons
    path("donation/", donation_view, name="donation"),
    path("donation/choice/", donation_payment_choice_view, name="donation_payment_choice"),
    path("donation/success/", donation_success_view, name="donation_success"),
    path("donation/cancel/", donation_cancel_view, name="donation_cancel"),
    path("public-donations/", public_donations_view, name="public_donations"),
    path("donation/history/", donation_history_view, name="donation_history"),
    path("donation/<int:donation_id>/receipt/", download_receipt_view, name="download_receipt"),

    # 💳 Intégrations Paiements
    path("payment/stripe/<int:donation_id>/", stripe_checkout_view, name="stripe_checkout"),
    path("payment/paypal/<int:donation_id>/", paypal_checkout_view, name="paypal_checkout"),
    path("payment/orange-money/<int:donation_id>/", orange_money_checkout_view, name="orange_money_checkout"),
    path("payment/wave/<int:donation_id>/", wave_checkout_view, name="wave_checkout"),
    path("payment/visa/<int:donation_id>/", visa_checkout_view, name="visa_checkout"),

    # 🔁 Webhooks
    path("webhooks/paypal/", PayPalWebhookView.as_view(), name="paypal_webhook"),
    path("webhooks/wave/", WaveWebhookView.as_view(), name="wave_webhook"),
    path("webhooks/orange/", OrangeMoneyWebhookView.as_view(), name="orange_webhook"),
    path("webhooks/stripe/", StripeWebhookView.as_view(), name="stripe_webhook"),

    # 💪 Engagement
    path("engagement/", engagement_view, name="engagement"),

    # 📰 Publications
    path("publications/", publication_list, name="publication_list"),
    path("publication/<int:pk>/request-access/", publication_request_access, name="publication_request_access"),
    path("publication/<int:pk>/pay/", publication_pay_and_request, name="publication_pay_and_request"),
    path("publication/<int:pk>/download/", download_publication, name="download_publication"),
    path('publication/<int:pk>/email_request/', publication_email_request, name='publication_email_request'),

    # 📁 Projets
    path("projects/", projects_list_view, name="projects_list"),
    path("projects/create/", create_project_view, name="create_project"),
    path("project/<int:pk>/", project_detail_view, name="project_detail"),
    path("projects/<int:pk>/edit/", update_project_view, name="update_project"),
    path("projects/<int:pk>/delete/", delete_project_view, name="delete_project"),

]
