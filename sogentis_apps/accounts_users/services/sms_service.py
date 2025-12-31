# accounts_users/services/sms_service.py
from django.conf import settings

def send_sms(phone, message):
    """
    Envoi de SMS.

    ⚠️ En développement/test : impression dans la console.
    ⚠️ En production : remplacer par un provider réel (Twilio, Orange, Infobip...).

    Exemple Twilio :
        from twilio.rest import Client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=message,
            from_=settings.TWILIO_FROM,
            to=str(phone)
        )
    """

    # =========================
    # MODE DÉVELOPPEMENT / TEST
    # =========================
    print(f"[SMS MOCK] {phone} → {message}")

    # =========================
    # MODE PRODUCTION (décommenter et configurer)
    # =========================
    # from twilio.rest import Client
    # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    # client.messages.create(
    #     body=message,
    #     from_=settings.TWILIO_FROM,
    #     to=str(phone)
    # )
