from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from economic.support.forms import TicketCreateForm, TicketMessageForm
from economic.support.models import SupportTicket
from economic.support.services import create_ticket, add_ticket_message, close_ticket


@login_required
def ticket_list_view(request):
    qs = SupportTicket.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "economic/support/tickets/ticket_list.html", {"tickets": qs})


@login_required
def ticket_create_view(request):
    if request.method == "POST":
        form = TicketCreateForm(request.POST)
        if form.is_valid():
            ticket = create_ticket(
                user=request.user,
                subject=form.cleaned_data["subject"],
                description=form.cleaned_data["description"],
                priority=form.cleaned_data["priority"],
                order_ref=form.cleaned_data.get("order_ref", ""),
            )
            messages.success(request, _("Ticket créé avec succès."))
            return redirect("support:ticket_detail", ticket_id=ticket.id)
    else:
        form = TicketCreateForm()

    return render(request, "economic/support/tickets/ticket_create.html", {"form": form})


def _get_user_ticket_or_404(request, ticket_id):
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    # Staff peut voir tout, sinon uniquement propriétaire
    if request.user.is_staff or request.user.is_superuser:
        return ticket
    if ticket.user_id != request.user.id:
        raise Http404
    return ticket


@login_required
def ticket_detail_view(request, ticket_id):
    ticket = _get_user_ticket_or_404(request, ticket_id)
    msg_form = TicketMessageForm()
    return render(
        request,
        "economic/support/tickets/ticket_detail.html",
        {"ticket": ticket, "msg_form": msg_form},
    )


@login_required
@require_POST
def ticket_add_message_view(request, ticket_id):
    ticket = _get_user_ticket_or_404(request, ticket_id)

    if ticket.status == SupportTicket.Status.CLOSED:
        messages.error(request, _("Ce ticket est clôturé."))
        return redirect("support:ticket_detail", ticket_id=ticket.id)

    form = TicketMessageForm(request.POST, request.FILES)
    if form.is_valid():
        is_staff_reply = bool(request.user.is_staff or request.user.is_superuser)
        add_ticket_message(
            ticket=ticket,
            author=request.user,
            message=form.cleaned_data["message"],
            attachment=form.cleaned_data.get("attachment"),
            is_staff_reply=is_staff_reply,
        )
        messages.success(request, _("Message envoyé."))
    else:
        messages.error(request, _("Veuillez corriger le formulaire."))

    return redirect("support:ticket_detail", ticket_id=ticket.id)


@login_required
@require_POST
def ticket_close_view(request, ticket_id):
    ticket = _get_user_ticket_or_404(request, ticket_id)

    # Client peut clôturer son ticket, staff aussi
    close_ticket(ticket=ticket)
    messages.success(request, _("Ticket clôturé."))
    return redirect("support:ticket_detail", ticket_id=ticket.id)
