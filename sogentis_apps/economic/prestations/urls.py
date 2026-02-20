# economic/prestations/urls.py
from __future__ import annotations

from django.urls import path

from .views import (
    index,
    prestation_detail,
    request_quote,
    tickets,
    package_detail,
    package_quote,
    offers,
    projects,
    payments,
)

app_name = "prestations"

urlpatterns = [
    # index
    path("", index.prestations_index_view, name="index"),

    # tickets
    path("tickets/", tickets.tickets_view, name="tickets"),

    # entitlements / downloads
    path("my-downloads/", offers.my_entitlements_view, name="my_downloads"),
    path("download/<uuid:token>/", offers.entitlement_download_view, name="download"),

    # projects (AO / appels d'offres)
    path("projects/", projects.projects_list_view, name="projects_list"),
    path("projects/new/", projects.project_create_view, name="projects_create"),
    path("projects/<slug:slug>/", projects.project_detail_view, name="projects_detail"),
    path("projects/<slug:slug>/bid/", projects.project_bid_view, name="projects_bid"),

    # packs
    path("packs/<slug:slug>/", package_detail.package_detail_view, name="package_detail"),
    path("packs/<slug:slug>/quote/", package_quote.package_quote_view, name="package_quote"),
    path("packs/<slug:slug>/pay/", payments.pay_package_start_view, name="pay_package"),  # ✅ NEW

    path("packs/<slug:slug>/offers/<slug:offer_slug>/", offers.package_offer_detail_view, name="package_offer_detail"),

    # prestation offers
    path("<slug:slug>/offers/<slug:offer_slug>/", offers.prestation_offer_detail_view, name="prestation_offer_detail"),

    # quote (prestation)
    path("<slug:slug>/quote/", request_quote.request_quote_view, name="quote"),
    path("<slug:slug>/pay/", payments.pay_prestation_start_view, name="pay_prestation"),  # ✅ NEW

    # detail (prestation) — toujours en dernier
    path("<slug:slug>/", prestation_detail.prestation_detail_view, name="detail"),
]








# # economic/prestations/urls.py
# from __future__ import annotations

# from django.urls import path

# from .views import (
#     index,
#     prestation_detail,
#     request_quote,
#     tickets,
#     package_detail,
#     package_quote,
# )

# app_name = "prestations"

# urlpatterns = [
#     # index
#     path("", index.prestations_index_view, name="index"),

#     # tickets
#     path("tickets/", tickets.tickets_view, name="tickets"),

#     # packs
#     path("packs/<slug:slug>/", package_detail.package_detail_view, name="package_detail"),
#     path("packs/<slug:slug>/quote/", package_quote.package_quote_view, name="package_quote"),

#     # quote (prestation)
#     path("<slug:slug>/quote/", request_quote.request_quote_view, name="quote"),

#     # detail (prestation) — toujours en dernier
#     path("<slug:slug>/", prestation_detail.prestation_detail_view, name="detail"),
# ]






# # economic/prestations/urls.py
# from django.urls import path

# from .views import (
#     index,
#     prestation_detail,
#     request_quote,
#     tickets,
#     package_detail,
#     package_quote,
# )

# app_name = "prestations"

# urlpatterns = [
#     path("", index.services_index_view, name="index"),

#     # routes fixes
#     path("tickets/", tickets.tickets_view, name="tickets"),

#     # packs (✅ ajout)
#     path("packs/<slug:slug>/", package_detail.package_detail_view, name="package_detail"),
#     path("packs/<slug:slug>/quote/", package_quote.package_quote_view, name="package_quote"),

#     # quote service
#     path("<slug:slug>/quote/", request_quote.request_quote_view, name="quote"),

#     # catch-all service detail en dernier
#     path("<slug:slug>/", prestation_detail.service_detail_view, name="detail"),
# ]




# # economic/services/urls.py
# from django.urls import path
# from .views import index, service_detail, request_quote, tickets

# app_name = "services"

# urlpatterns = [
#     path("", index.services_index_view, name="index"),

#     # IMPORTANT : routes fixes avant le slug
#     path("tickets/", tickets.tickets_view, name="tickets"),
#     path("<slug:slug>/quote/", request_quote.request_quote_view, name="quote"),

#     # Catch-all pour les détails de service en dernier
#     path("<slug:slug>/", service_detail.service_detail_view, name="detail"),
# ]







# # /economic/services/urls.py
# from django.urls import path
# from .views import index, service_detail, request_quote, tickets

# app_name = "services"

# urlpatterns = [
#     path("", index.services_index_view, name="index"),
#     path("<slug:slug>/", service_detail.service_detail_view, name="detail"),
#     path("<slug:slug>/quote/", request_quote.request_quote_view, name="quote"),
#     path("tickets/", tickets.tickets_view, name="tickets"),
# ]

