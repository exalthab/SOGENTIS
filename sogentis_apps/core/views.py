from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _

from .forms import ContactForm


def home_view(request):
    """Render the home page."""
    return render(request, "core/home.html")

def privacy_policy(request):
    return render(request, "core/privacy.html")

def cgu(request):
    return render(request, "core/cgu.html")

def cookies_policy(request):
    return render(request, "core/cookies.html")

def contact_view(request):
    """Handle the contact form submission."""
    form = ContactForm(request.POST or None)

    if form.is_valid():
        name = form.cleaned_data["name"]
        email = form.cleaned_data["email"]
        message = form.cleaned_data["message"]

        full_message = f"Message de {name} <{email}>:\n\n{message}"

        try:
            send_mail(
                subject="Nouveau message via le formulaire de contact",
                message=full_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_EMAIL],
                fail_silently=False,
            )
            messages.success(request, "Votre message a bien été envoyé. Merci !")
        except Exception as e:
            messages.error(request, f"Une erreur est survenue : {str(e)}")

        return redirect(
            "contact"
        )

    return render(request, "core/contact.html", {"form": form})


