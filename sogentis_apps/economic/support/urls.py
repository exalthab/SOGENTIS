# /economic/support/urls.py
from django.urls import path

from economic.support.web.views.tickets import (
    ticket_list_view,
    ticket_create_view,
    ticket_detail_view,
    ticket_add_message_view,
    ticket_close_view,
)
from economic.support.web.views.faq import faq_list_view
from django.shortcuts import render

app_name = "support"

def support_index_view(request):
    return render(request, "economic/support/index.html")

urlpatterns = [
    path("", support_index_view, name="index"),

    path("tickets/", ticket_list_view, name="ticket_list"),
    path("tickets/new/", ticket_create_view, name="ticket_create"),
    path("tickets/<uuid:ticket_id>/", ticket_detail_view, name="ticket_detail"),
    path("tickets/<uuid:ticket_id>/message/", ticket_add_message_view, name="ticket_add_message"),
    path("tickets/<uuid:ticket_id>/close/", ticket_close_view, name="ticket_close"),

    path("faq/", faq_list_view, name="faq_list"),
]









# from django.urls import path
# from .views.index import resources_index_view

# app_name = "support"

# urlpatterns = [
#     path("", resources_index_view, name="index"),
# ]
