# social/views/download.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.http import FileResponse, Http404
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.apps import apps
from django.utils import timezone

import os
import secrets

from social.models import Publication  # adapte l'import à ton projet
from social.models.download_token import DownloadToken
from social.forms import DownloadCodeForm

def _get_model(app_label, model_name):
    """
    Récupère un modèle de façon résiliente et lève une erreur claire s'il manque.
    """
    try:
        return apps.get_model(app_label, model_name)
    except LookupError as e:
        raise RuntimeError(
            f"Le modèle {app_label}.{model_name} est introuvable. "
            f"Assure-toi qu'il existe et que l'app '{app_label}' est dans INSTALLED_APPS. "
            f"Crée le fichier du modèle et lance les migrations."
        ) from e


def _now():
    return timezone.now()


def _generate_download_token(user, document, validity_hours=24):
    """
    Crée un token de téléchargement. Suppose que le modèle DownloadToken
    possède les champs : user (FK), document (FK), token (CharField),
    expires_at (DateTimeField, nullable), used (BooleanField).
    """
    DownloadToken = _get_model("social", "DownloadToken")
    token_str = secrets.token_urlsafe(32)
    expires_at = _now() + timezone.timedelta(hours=validity_hours)
    return DownloadToken.objects.create(
        user=user,
        document=document,
        token=token_str,
        expires_at=expires_at,
        used=False,
    )


def _is_token_valid(token_obj):
    """Vérifie la validité d'un token (non utilisé et non expiré)."""
    if not token_obj:
        return False
    if getattr(token_obj, "used", True):
        return False
    expires_at = getattr(token_obj, "expires_at", None)
    return expires_at is None or expires_at > _now()


@login_required
def send_download_code(request, doc_id):
    Publication = _get_model("social", "Publication")
    document = get_object_or_404(Publication, pk=doc_id)

    token = _generate_download_token(request.user, document, validity_hours=24)

    send_mail(
        subject=_("Votre code de téléchargement"),
        message=_(
            "Voici votre code pour re-télécharger « %(title)s » : %(code)s\n\n"
            "Ce code expirera dans 24 heures."
        )
        % {"title": document.title, "code": token.token},
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
        recipient_list=[request.user.email],
    )

    messages.success(request, _("Un code a été envoyé à votre email."))
    return redirect("social:enter_download_code")


@login_required
def enter_download_code(request):
    # Import tardif pour éviter d'échouer au start si le formulaire n'existe pas encore.
    from social.forms import DownloadCodeForm  # noqa: WPS433

    DownloadToken = _get_model("social", "DownloadToken")

    if request.method == "POST":
        form = DownloadCodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"].strip()
            token = (
                DownloadToken.objects.select_related("document")
                .filter(token=code, user=request.user)
                .first()
            )

            if not _is_token_valid(token):
                messages.error(request, _("Code invalide, expiré ou déjà utilisé."))
                return redirect("social:enter_download_code")

            # Marquer comme utilisé
            token.used = True
            token.save(update_fields=["used"])

            # Récupération du fichier (adapte le nom du champ si besoin)
            file_field = getattr(token.document, "file", None)
            file_path = getattr(file_field, "path", None)

            if not file_path or not os.path.exists(file_path):
                raise Http404(_("Fichier introuvable."))

            return FileResponse(
                open(file_path, "rb"),
                as_attachment=True,
                filename=os.path.basename(file_path),
            )
    else:
        form = DownloadCodeForm()

    return render(request, "social/enter_download_code.html", {"form": form})
