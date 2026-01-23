# economic/formations/services/certificate_pdf.py
from __future__ import annotations

import io
from typing import Optional

from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone
from django.utils.translation import gettext as _

from economic.formations.models import Certificate


def _user_display_name(user) -> str:
    for attr in ("get_full_name", "get_short_name"):
        fn = getattr(user, attr, None)
        if callable(fn):
            val = (fn() or "").strip()
            if val:
                return val
    return (getattr(user, "email", "") or getattr(user, "username", "") or str(user)).strip()


def _course_title(course) -> str:
    # Parler: course.title fonctionne en template, mais côté python, safe getter si dispo
    getter = getattr(course, "safe_translation_getter", None)
    if callable(getter):
        return getter("title", any_language=True) or str(course)
    return getattr(course, "title", None) or str(course)


def generate_certificate_pdf_and_attach(
    certificate: Certificate,
    *,
    force: bool = False,
) -> bool:
    """
    Génère un PDF (ReportLab) et l'attache à certificate.pdf_file.
    Retourne True si un PDF a été généré/attaché, sinon False.

    - Ne régénère pas si pdf_file existe déjà (sauf force=True)
    - Ne génère pas si certificate.revoked=True
    """
    if certificate.revoked:
        return False

    if certificate.pdf_file and not force:
        return False

    # Import reportlab ici pour éviter un import lourd au boot
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4

    project_name = getattr(settings, "PROJECT_NAME", "SOGENTIS")
    site_url = getattr(settings, "SITE_URL", "")  # optionnel
    issued_dt = timezone.localtime(certificate.issued_at) if certificate.issued_at else timezone.localtime(timezone.now())

    user = certificate.enrollment.user
    course = certificate.course

    learner_name = _user_display_name(user)
    course_title = _course_title(course)

    # --- Fond + marges
    margin_x = 18 * mm
    margin_top = 18 * mm
    margin_bottom = 18 * mm

    # --- Cadre
    c.setLineWidth(1)
    c.rect(margin_x, margin_bottom, width - 2 * margin_x, height - margin_top - margin_bottom)

    # --- Logo (si disponible)
    # Mets un logo optionnel via settings.FORMATIONS_CERT_LOGO (chemin absolu ou relatif MEDIA/STATIC)
    logo_path = getattr(settings, "FORMATIONS_CERT_LOGO", None)
    if logo_path:
        try:
            logo = ImageReader(logo_path)
            c.drawImage(logo, margin_x + 10 * mm, height - margin_top - 22 * mm, width=28 * mm, height=28 * mm, mask="auto")
        except Exception:
            pass

    # --- Titre
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(width / 2, height - margin_top - 20 * mm, _("CERTIFICAT"))

    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, height - margin_top - 30 * mm, _("Atteste que"))

    # --- Nom apprenant
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, height - margin_top - 44 * mm, learner_name)

    # --- Texte
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, height - margin_top - 58 * mm, _("a complété avec succès la formation"))

    # --- Titre cours
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - margin_top - 72 * mm, course_title)

    # --- Détails
    c.setFont("Helvetica", 10)
    c.drawString(margin_x + 10 * mm, margin_bottom + 22 * mm, f"{_('Code')}: {certificate.code}")
    c.drawString(margin_x + 10 * mm, margin_bottom + 16 * mm, f"{_('UUID')}: {certificate.uuid}")
    c.drawString(margin_x + 10 * mm, margin_bottom + 10 * mm, f"{_('Date')}: {issued_dt:%d/%m/%Y}")

    # --- URL de vérification (optionnel)
    if site_url:
        c.drawRightString(width - margin_x - 10 * mm, margin_bottom + 10 * mm, f"{_('Vérification')}: {site_url}")

    # --- QR Code (optionnel)
    try:
        from reportlab.graphics.barcode import qr
        qr_value = f"{project_name} | {certificate.code} | {certificate.uuid}"
        q = qr.QrCodeWidget(qr_value)
        bounds = q.getBounds()
        size = 26 * mm
        w = bounds[2] - bounds[0]
        h = bounds[3] - bounds[1]
        d = size / max(w, h)
        from reportlab.graphics.shapes import Drawing
        from reportlab.graphics import renderPDF

        drawing = Drawing(size, size, transform=[d, 0, 0, d, 0, 0])
        drawing.add(q)
        renderPDF.draw(drawing, c, width - margin_x - 10 * mm - size, margin_bottom + 12 * mm)
    except Exception:
        pass

    # --- Footer
    c.setFont("Helvetica-Oblique", 9)
    c.drawCentredString(width / 2, margin_bottom + 6 * mm, f"{project_name} — {_('Formation & Certification')}")

    c.showPage()
    c.save()

    pdf_bytes = buf.getvalue()
    buf.close()

    filename = getattr(certificate, "download_filename", None)
    filename = filename() if callable(filename) else f"certificate-{certificate.code}.pdf"

    certificate.pdf_file.save(filename, ContentFile(pdf_bytes), save=True)
    return True
