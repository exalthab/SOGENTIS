# social/views/publication_view.py
import logging
import mimetypes

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import FileResponse, Http404
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.urls import reverse
from django.conf import settings
from django.db import transaction

# ✅ Importe les modèles depuis le __init__ central
from social.models import Publication, PublicationPurchase
from social.models import DocumentPurchase  # legacy (ancien système)

logger = logging.getLogger(__name__)


def _get_user_purchase_for_doc(user, doc):
    """
    Retourne (purchase_obj, source) pour l'utilisateur et le document donnés.
    - source = "new" si PublicationPurchase, "legacy" si DocumentPurchase, sinon None.
    """
    if not user or not user.is_authenticated:
        return None, None

    try:
        # Nouveau système prioritaire
        pp = PublicationPurchase.objects.filter(user=user, document=doc).first()
        if pp:
            return pp, "new"
    except Exception:
        # log et fallback
        logger.exception("Error while querying PublicationPurchase for user=%s doc=%s", getattr(user, "id", None), getattr(doc, "id", None))

    try:
        # Ancien système (legacy)
        lp = DocumentPurchase.objects.filter(user=user, publication=doc).first()
        if lp:
            return lp, "legacy"
    except Exception:
        logger.exception("Error while querying DocumentPurchase (legacy) for user=%s doc=%s", getattr(user, "id", None), getattr(doc, "id", None))

    return None, None


def _attach_file_to_email(email, file_field):
    """
    Lit le fichier lié au `file_field` et l'attache à l'EmailMessage.
    Protège contre les erreurs et gère le type MIME par défaut.
    """
    if not file_field:
        return
    try:
        with file_field.open("rb") as f:
            file_content = f.read()
        filename = getattr(file_field, "name", "attachment")
        mime_type, _ = mimetypes.guess_type(filename)
        email.attach(filename.split("/")[-1], file_content, mime_type or "application/octet-stream")
    except FileNotFoundError:
        logger.warning("Fichier non trouvé lors de l'attachement à l'email: %s", getattr(file_field, "name", None))
    except Exception as e:
        logger.exception("Erreur lors de l'attachement du fichier à l'email: %s", e)


def _send_publication_email(user, publication, copy_number):
    """
    Envoie un email HTML à l'utilisateur avec la copie demandée (si publication.file présent).
    Retourne True si l'envoi a été tenté (même si send() a échoué), False si pas de fichier à envoyer.
    """
    if not publication or not publication.file:
        return False

    mail_subject = f"Votre document demandé – {publication.title}"
    mail_body = render_to_string(
        "social/email_document.html",
        {"user": user, "doc": publication, "copy_number": copy_number},
    )

    to_addr = getattr(user, "email", None)
    if not to_addr:
        logger.warning("Utilisateur sans email : cannot send publication email (user=%s)", getattr(user, "id", None))
        return False

    email = EmailMessage(mail_subject, mail_body, to=[to_addr])
    email.content_subtype = "html"
    # from email fallback
    if hasattr(settings, "DEFAULT_FROM_EMAIL"):
        email.from_email = settings.DEFAULT_FROM_EMAIL

    _attach_file_to_email(email, publication.file)

    try:
        email.send(fail_silently=False)
        logger.info("Envoi d'email pour publication id=%s à %s (copy=%s)", getattr(publication, "id", None), to_addr, copy_number)
    except Exception as e:
        logger.exception("Erreur d'envoi d'email pour publication id=%s to=%s : %s", getattr(publication, "id", None), to_addr, e)
    return True


def publication_list(request):
    """
    Affiche la liste paginée des publications publiques.
    Pour chaque doc : .purchased, .purchase_obj et .has_downloaded (legacy uniquement).
    """
    publications_qs = Publication.objects.filter(is_public=True).order_by("-created_at")
    page = request.GET.get("page", 1)
    paginator = Paginator(publications_qs, 10)
    try:
        publications_page = paginator.page(page)
    except PageNotAnInteger:
        publications_page = paginator.page(1)
    except EmptyPage:
        publications_page = paginator.page(paginator.num_pages)

    publications_data = []
    if request.user.is_authenticated:
        # ✅ Admin/staff : toujours accès
        if request.user.is_staff or request.user.is_superuser:
            for doc in publications_page:
                doc.purchased = True
                doc.purchase_obj = None
                doc.has_downloaded = False
                publications_data.append(doc)
        else:
            for doc in publications_page:
                purchase_obj, source = _get_user_purchase_for_doc(request.user, doc)
                doc.purchased = purchase_obj is not None
                doc.purchase_obj = purchase_obj
                # has_downloaded uniquement pertinent pour le legacy
                doc.has_downloaded = bool(getattr(purchase_obj, "has_downloaded", False)) if source == "legacy" else False
                publications_data.append(doc)
    else:
        publications_data = list(publications_page)

    context = {
        "publications": publications_data,
        "paginator": paginator,
        "page_obj": publications_page,
    }
    return render(request, "social/publications.html", context)


@login_required
def publication_request_access(request, pk):
    # ✅ Admin/staff : accès sans restriction
    if request.user.is_staff or request.user.is_superuser:
        return redirect("social:publication_pay_and_request", pk=pk)

    publication = get_object_or_404(Publication, pk=pk, is_public=True)
    if request.method == "POST":
        return redirect("social:publication_pay_and_request", pk=pk)
    return render(request, "social/publication_access_request.html", {"doc": publication})


@login_required
def publication_pay_and_request(request, pk):
    """
    Valide l'achat (démo) et attribue un numéro de copie selon l'ordre d'achat.
    - Nouveau système : PublicationPurchase.create_with_next_number(user, document)
    - Si achat existant (nouveau/legacy), on réaffiche la confirmation avec le numéro existant.
    """
    # ✅ Admin/staff : accès gratuit & immédiat
    if request.user.is_staff or request.user.is_superuser:
        publication = get_object_or_404(Publication, pk=pk, is_public=True)
        return render(
            request,
            "social/document_paid_success.html",
            {"doc": publication, "already_bought": True, "copy_number": "ADMIN"},
        )

    publication = get_object_or_404(Publication, pk=pk, is_public=True)
    price = 2000  # FCFA (démo)

    # Vérifier si l'utilisateur a déjà acheté (nouveau système en priorité)
    existing_purchase, source = _get_user_purchase_for_doc(request.user, publication)
    if existing_purchase:
        copy_number = getattr(existing_purchase, "copy_number", None) or "—"
        return render(
            request,
            "social/document_paid_success.html",
            {"doc": publication, "already_bought": True, "copy_number": copy_number},
        )

    if request.method == "POST":
        # Tentative d'utiliser la méthode fournie (qui devrait être atomique).
        new_purchase = None
        try:
            if hasattr(PublicationPurchase, "create_with_next_number"):
                # on utilise la méthode du modèle si disponible
                new_purchase = PublicationPurchase.create_with_next_number(user=request.user, document=publication)
            else:
                # fallback : création manuelle de la prochaine copie (non-atomique si pas transaction)
                with transaction.atomic():
                    last = PublicationPurchase.objects.filter(document=publication).order_by("-copy_number").first()
                    next_number = (last.copy_number + 1) if last and last.copy_number else 1
                    new_purchase = PublicationPurchase.objects.create(
                        user=request.user,
                        document=publication,
                        email=request.user.email,
                        amount_paid=price,
                        payment_method="demo",
                        payment_id="demo-id",
                        copy_number=next_number,
                    )
        except Exception as e:
            logger.exception("Erreur lors de la création d'un PublicationPurchase pour user=%s doc=%s: %s", getattr(request.user, "id", None), getattr(publication, "id", None), e)
            # affiche erreur simple à l'utilisateur (tu peux remplacer par messages.error)
            return render(request, "social/publication_pay_request.html", {"doc": publication, "price": price, "error": _("Impossible de traiter votre demande pour le moment.")})

        # Envoi mail avec la référence de copie (pièce jointe si présente)
        try:
            _send_publication_email(request.user, publication, getattr(new_purchase, "copy_number", "—"))
        except Exception:
            # _send_publication_email encapsule déjà logs, on protège quand même
            logger.exception("Erreur lors de l'envoi de l'email après achat pour user=%s doc=%s", getattr(request.user, "id", None), getattr(publication, "id", None))

        return render(
            request,
            "social/document_paid_success.html",
            {"doc": publication, "already_bought": False, "copy_number": getattr(new_purchase, "copy_number", "—")},
        )

    return render(request, "social/publication_pay_request.html", {"doc": publication, "price": price})


@login_required
def download_publication(request, pk):
    """
    Téléchargement direct :
    - ✅ Admin/staff : autorisé (bypass).
    - 👤 Utilisateur : on redirige vers l’envoi d’un code (nouveau flux sécurisé).
    """
    publication = get_object_or_404(Publication, pk=pk, is_public=True)

    # Admin/staff : autorisé
    if request.user.is_staff or request.user.is_superuser:
        if not publication.file:
            raise Http404(_("Fichier non trouvé"))
        filename = publication.file.name.split("/")[-1]
        try:
            return FileResponse(publication.file.open("rb"), as_attachment=True, filename=filename)
        except FileNotFoundError:
            logger.warning("Fichier non trouvé quand on tente d'ouvrir pour download: %s", getattr(publication.file, "name", None))
            raise Http404(_("Fichier non trouvé"))
        except Exception as e:
            logger.exception("Erreur lors du FileResponse pour publication id=%s: %s", getattr(publication, "id", None), e)
            raise Http404(_("Erreur de téléchargement"))

    # Utilisateur : redirige vers le flux "envoyer un code"
    # On passe doc_id pour compatibilité avec ton ancien code
    return redirect("social:send_download_code", doc_id=pk)


@login_required
def publication_email_request(request, pk):
    """
    Ré-envoi par email (support). Fonctionne si l'utilisateur a acheté (nouveau ou legacy).
    - Admin/staff : envoi direct sans vérif.
    """
    publication = get_object_or_404(Publication, pk=pk, is_public=True)

    # Admin/staff : envoi direct
    if request.user.is_staff or request.user.is_superuser:
        if publication.file and request.method == "POST":
            try:
                _send_publication_email(request.user, publication, "ADMIN")
            except Exception:
                logger.exception("Erreur lors de l'envoi email pour staff/admin (doc=%s)", getattr(publication, "id", None))
            return render(request, "social/document_email_resent.html", {"doc": publication, "copy_number": "ADMIN"})
        return render(request, "social/request_document_email.html", {"doc": publication})

    # Utilisateur : doit avoir acheté (nouveau ou legacy)
    purchase_obj, _source = _get_user_purchase_for_doc(request.user, publication)
    if not purchase_obj:
        return redirect("social:publication_pay_and_request", pk=pk)

    if request.method == "POST":
        copy_number = getattr(purchase_obj, "copy_number", None) or "—"
        try:
            _send_publication_email(request.user, publication, copy_number)
        except Exception:
            logger.exception("Erreur lors de l'envoi d'email de ré-envoi pour user=%s doc=%s", getattr(request.user, "id", None), getattr(publication, "id", None))
        return render(request, "social/document_email_resent.html", {"doc": publication, "copy_number": copy_number})

    return render(request, "social/request_document_email.html", {"doc": publication})
