from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from django.conf import settings


def send_profile_status_email(user, status):
    """
    Envoie l’e-mail correspondant au statut du profil :
    - approved  → profile_approved.html
    - rejected  → profile_rejected.html
    """

    if status == "approved":
        subject = _("Votre profil a été validé")
        template = "accounts_users/emails/profile_approved.html"

    elif status == "rejected":
        subject = _("Votre profil a été refusé")
        template = "accounts_users/emails/profile_rejected.html"

    else:
        # pending ou statut inconnu → aucun email
        return

    context = {
        "user": user,
        "site_name": getattr(settings, "PROJECT_NAME", "SOGENTIS"),
    }

    html_message = render_to_string(template, context)
    plain_message = _(
        "Merci de consulter votre espace SOGENTIS pour plus d’informations."
    )

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )






# # accounts_users/services/profile_validation_service.py
# from django.core.mail import send_mail
# from django.template.loader import render_to_string
# from django.utils.translation import gettext as _
# from django.conf import settings

# def send_profile_status_email(user, status):
#     """
#     Envoie l’e-mail correspondant :
#     - approved → profile_approved.html
#     - refused → profile_refused.html
#     """

#     if status == "approved":
#         subject = _("Votre profil a été validé")
#         template = "accounts_users/emails/profile_approved.html"

#     elif status == "refused":
#         subject = _("Votre profil a été refusé")
#         template = "accounts_users/emails/profile_refused.html"

#     else:
#         return

#     html_message = render_to_string(template, {"user": user})
#     plain_message = _("Merci de consulter votre espace SOGENTIS pour plus d’informations.")

#     send_mail(
#         subject=subject,
#         message=plain_message,
#         from_email=settings.DEFAULT_FROM_EMAIL,
#         recipient_list=[user.email],
#         html_message=html_message,
#         fail_silently=False,
#     )
