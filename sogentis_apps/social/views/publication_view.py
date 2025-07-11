from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import FileResponse, Http404
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import mimetypes

from social.models.publication import Publication
from social.models.document_access import DocumentPurchase

def publication_list(request):
    """
    Affiche la liste paginée des publications publiques.
    Passe pour chaque doc la propriété .purchased, .purchase_obj et .has_downloaded
    """
    publications_qs = Publication.objects.filter(is_public=True).order_by('-created_at')
    page = request.GET.get('page', 1)
    paginator = Paginator(publications_qs, 10)
    try:
        publications_page = paginator.page(page)
    except PageNotAnInteger:
        publications_page = paginator.page(1)
    except EmptyPage:
        publications_page = paginator.page(paginator.num_pages)

    publications_data = []
    if request.user.is_authenticated:
        # ✅ Admin/staff : toujours accès sans restriction
        if request.user.is_staff or request.user.is_superuser:
            for doc in publications_page:
                doc.purchased = True
                doc.purchase_obj = None
                doc.has_downloaded = False
                publications_data.append(doc)
        else:
            purchases = {p.publication_id: p for p in DocumentPurchase.objects.filter(user=request.user)}
            for doc in publications_page:
                doc.purchased = doc.pk in purchases
                doc.purchase_obj = purchases.get(doc.pk)
                doc.has_downloaded = getattr(doc.purchase_obj, "has_downloaded", False) if doc.purchase_obj else False
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
    # ✅ Admin/staff : accès sans restriction
    if request.user.is_staff or request.user.is_superuser:
        return redirect('social:publication_pay_and_request', pk=pk)

    publication = get_object_or_404(Publication, pk=pk, is_public=True)
    if request.method == "POST":
        return redirect("social:publication_pay_and_request", pk=pk)
    return render(request, "social/publication_access_request.html", {"doc": publication})

@login_required
def publication_pay_and_request(request, pk):
    # ✅ Admin/staff : accès sans restriction, accès gratuit
    if request.user.is_staff or request.user.is_superuser:
        publication = get_object_or_404(Publication, pk=pk, is_public=True)
        return render(request, "social/document_paid_success.html", {
            "doc": publication,
            "already_bought": True,
            "copy_number": "ADMIN"
        })

    publication = get_object_or_404(Publication, pk=pk, is_public=True)
    price = 2000  # FCFA

    # Vérifier si l'utilisateur a déjà acheté ce document
    already_bought = DocumentPurchase.objects.filter(
        user=request.user,
        publication=publication
    ).first()

    if already_bought:
        return render(request, "social/document_paid_success.html", {
            "doc": publication,
            "already_bought": True,
            "copy_number": already_bought.copy_number
        })

    if request.method == "POST":
        last = DocumentPurchase.objects.filter(
            publication=publication
        ).order_by('-copy_number').first()
        next_number = (last.copy_number + 1) if last and last.copy_number else 1

        purchase = DocumentPurchase.objects.create(
            user=request.user,
            publication=publication,
            email=request.user.email,
            amount_paid=price,
            payment_method="stripe",
            payment_id="demo-id",
            copy_number=next_number,
            has_downloaded=False
        )

        # Envoi mail avec la référence de copie
        if publication.file:
            mail_subject = f"Votre document demandé – {publication.title}"
            mail_body = render_to_string(
                "social/email_document.html",
                {
                    "user": request.user,
                    "doc": publication,
                    "copy_number": purchase.copy_number
                }
            )
            email = EmailMessage(
                mail_subject,
                mail_body,
                to=[request.user.email]
            )
            file_obj = publication.file.open("rb")
            file_content = file_obj.read()
            file_obj.close()
            mime_type, _ = mimetypes.guess_type(publication.file.name)
            email.attach(publication.file.name, file_content, mime_type or "application/pdf")
            email.content_subtype = "html"
            email.send()

        return render(request, "social/document_paid_success.html", {
            "doc": publication,
            "already_bought": False,
            "copy_number": purchase.copy_number
        })

    return render(request, "social/publication_pay_request.html", {
        "doc": publication,
        "price": price
    })

@login_required
def download_publication(request, pk):
    # ✅ Admin/staff : accès sans restriction, toujours téléchargeable
    if request.user.is_staff or request.user.is_superuser:
        publication = get_object_or_404(Publication, pk=pk, is_public=True)
        if not publication.file:
            raise Http404(_("Fichier non trouvé"))
        filename = publication.file.name.split("/")[-1]
        return FileResponse(publication.file.open("rb"), as_attachment=True, filename=filename)

    publication = get_object_or_404(Publication, pk=pk, is_public=True)
    purchase = DocumentPurchase.objects.filter(user=request.user, publication=publication).first()
    if not purchase:
        return redirect('social:publication_pay_and_request', pk=pk)
    if not publication.file:
        raise Http404(_("Fichier non trouvé"))

    if purchase.has_downloaded:
        return redirect('social:publication_email_request', pk=pk)

    purchase.has_downloaded = True
    purchase.save(update_fields=["has_downloaded"])
    filename = publication.file.name.split("/")[-1]
    return FileResponse(publication.file.open("rb"), as_attachment=True, filename=filename)

@login_required
def publication_email_request(request, pk):
    # ✅ Admin/staff : accès sans restriction, envoi du fichier directement
    if request.user.is_staff or request.user.is_superuser:
        publication = get_object_or_404(Publication, pk=pk, is_public=True)
        if publication.file and request.method == "POST":
            mail_subject = f"Votre document demandé – {publication.title}"
            mail_body = render_to_string(
                "social/email_document.html",
                {"user": request.user, "doc": publication, "copy_number": "ADMIN"}
            )
            email = EmailMessage(
                mail_subject,
                mail_body,
                to=[request.user.email]
            )
            file_obj = publication.file.open("rb")
            file_content = file_obj.read()
            file_obj.close()
            mime_type, _ = mimetypes.guess_type(publication.file.name)
            email.attach(publication.file.name, file_content, mime_type or "application/pdf")
            email.content_subtype = "html"
            email.send()
            return render(request, "social/document_email_resent.html", {"doc": publication, "copy_number": "ADMIN"})
        return render(request, "social/request_document_email.html", {"doc": publication})

    publication = get_object_or_404(Publication, pk=pk, is_public=True)
    purchase = DocumentPurchase.objects.filter(user=request.user, publication=publication).first()
    if not purchase:
        return redirect('social:publication_pay_and_request', pk=pk)
    if request.method == "POST":
        copy_number = purchase.copy_number if purchase else ""
        if publication.file:
            mail_subject = f"Votre document demandé – {publication.title}"
            mail_body = render_to_string(
                "social/email_document.html",
                {"user": request.user, "doc": publication, "copy_number": copy_number}
            )
            email = EmailMessage(
                mail_subject,
                mail_body,
                to=[request.user.email]
            )
            file_obj = publication.file.open("rb")
            file_content = file_obj.read()
            file_obj.close()
            mime_type, _ = mimetypes.guess_type(publication.file.name)
            email.attach(publication.file.name, file_content, mime_type or "application/pdf")
            email.content_subtype = "html"
            email.send()
        return render(request, "social/document_email_resent.html", {"doc": publication, "copy_number": copy_number})
    return render(request, "social/request_document_email.html", {"doc": publication})
