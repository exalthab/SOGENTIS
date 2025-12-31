from django.utils import timezone

from economic.support.models import SupportTicket, TicketMessage


def create_ticket(*, user, subject: str, description: str, priority: str, order_ref: str = "") -> SupportTicket:
    return SupportTicket.objects.create(
        user=user,
        subject=subject,
        description=description,
        priority=priority,
        order_ref=order_ref or "",
    )


def add_ticket_message(*, ticket: SupportTicket, author, message: str, attachment=None, is_staff_reply: bool = False) -> TicketMessage:
    # simple logique: si staff répond -> IN_PROGRESS / si client répond -> WAITING_CUSTOMER (optionnel)
    if is_staff_reply and ticket.status in [SupportTicket.Status.OPEN, SupportTicket.Status.WAITING_CUSTOMER]:
        ticket.status = SupportTicket.Status.IN_PROGRESS
        ticket.save(update_fields=["status", "updated_at"])
    elif (not is_staff_reply) and ticket.status == SupportTicket.Status.IN_PROGRESS:
        ticket.status = SupportTicket.Status.WAITING_CUSTOMER
        ticket.save(update_fields=["status", "updated_at"])

    return TicketMessage.objects.create(
        ticket=ticket,
        author=author,
        is_staff_reply=is_staff_reply,
        message=message,
        attachment=attachment,
    )


def close_ticket(*, ticket: SupportTicket) -> SupportTicket:
    ticket.status = SupportTicket.Status.CLOSED
    ticket.closed_at = timezone.now()
    ticket.save(update_fields=["status", "closed_at", "updated_at"])
    return ticket
