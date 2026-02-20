# economic/formations/views/certificates.py
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from ..models import Certificate


@login_required
def certificates_view(request):
    certificates = (
        Certificate.objects
        .filter(enrollment__user=request.user, revoked=False)
        .select_related("enrollment", "course")
        .order_by("-issued_at")
    )
    return render(
        request,
        "economic/formations/learner/certificates_list.html",
        {"certificates": certificates},
    )


@login_required
def certificate_detail_view(request, uuid):
    certificate = get_object_or_404(
        Certificate.objects.select_related("enrollment", "course"),
        uuid=uuid,
        enrollment__user=request.user,
    )
    return render(
        request,
        "economic/formations/learner/certificate_detail.html",
        {"certificate": certificate},
    )


@login_required
def certificate_download_view(request, uuid):
    certificate = get_object_or_404(
        Certificate.objects.select_related("enrollment", "course"),
        uuid=uuid,
        enrollment__user=request.user,
        revoked=False,
    )

    if not certificate.pdf_file:
        messages.warning(request, _("Le PDF n’est pas encore disponible."))
        return redirect("economic:formations:certificate_detail", uuid=certificate.uuid)

    filename = "certificate.pdf"
    try:
        filename = certificate.download_filename() or filename
    except Exception:
        filename = filename

    try:
        f = certificate.pdf_file.open("rb")
    except Exception:
        raise Http404(_("Fichier introuvable."))

    return FileResponse(f, as_attachment=True, filename=filename)






# # economic/formations/views/certificates.py
# from django.contrib.auth.decorators import login_required
# from django.http import FileResponse, Http404
# from django.shortcuts import get_object_or_404, redirect, render
# from django.contrib import messages
# from django.utils.translation import gettext as _

# from ..models import Certificate


# @login_required
# def certificates_view(request):
#     certs = Certificate.objects.filter(enrollment__user=request.user, revoked=False).select_related(
#         "enrollment", "course"
#     ).order_by("-issued_at")
#     return render(request, "economic/formations/learner/certificates_list.html", {"certificates": certs})


# @login_required
# def certificate_detail_view(request, uuid):
#     cert = get_object_or_404(Certificate, uuid=uuid, enrollment__user=request.user)
#     return render(request, "economic/formations/learner/certificate_detail.html", {"certificate": cert})


# @login_required
# def certificate_download_view(request, uuid):
#     cert = get_object_or_404(Certificate, uuid=uuid, enrollment__user=request.user, revoked=False)

#     if not cert.pdf_file:
#         messages.warning(request, _("Le PDF n’est pas encore disponible."))
#         return redirect("economic:formations:certificate_detail", uuid=cert.uuid)

#     try:
#         return FileResponse(cert.pdf_file.open("rb"), as_attachment=True, filename=cert.download_filename())
#     except Exception as exc:
#         raise Http404(str(exc)) from exc




# from django.shortcuts import render


# def certificates_view(request):
#     return render(request, "formations/certificates.html")
