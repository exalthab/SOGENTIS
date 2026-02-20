# economic/ecommerce/views/invoice.py
from __future__ import annotations

from datetime import timedelta
from io import BytesIO
from pathlib import Path
from typing import Any

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext as _

from ..models.order import Order

# =========================================================
# PDF availability
# =========================================================
try:
    from xhtml2pdf import pisa  # type: ignore
    HAS_PDF = True
except Exception:
    HAS_PDF = False


# =========================================================
# STATIC & MEDIA resolution (xhtml2pdf compatible)
# =========================================================
def _static_abs(rel: str) -> str:
    """
    Retourne un chemin absolu vers un fichier statique.
    - prod: STATIC_ROOT
    - dev: STATICFILES_DIRS
    """
    rel = str(rel).lstrip("/").replace("\\", "/")

    static_root = Path(getattr(settings, "STATIC_ROOT", "") or "")
    if static_root:
        p = static_root / rel
        if p.exists():
            return str(p.resolve())

    for d in getattr(settings, "STATICFILES_DIRS", []) or []:
        p = Path(d) / rel
        if p.exists():
            return str(p.resolve())

    return ""


def _link_callback(uri: str, rel: str | None = None) -> str:
    """
    Convertit les URLs (static/media) en chemins locaux
    requis par xhtml2pdf.
    """
    uri = (uri or "").replace("\\", "/").strip()

    # Chemin absolu déjà valide
    try:
        p = Path(uri)
        if p.is_absolute() and p.exists():
            return str(p)
    except Exception:
        pass

    # STATIC_URL
    static_url = (getattr(settings, "STATIC_URL", "/static/") or "/static/").rstrip("/") + "/"
    if uri.startswith(static_url):
        abs_path = _static_abs(uri[len(static_url):])
        if abs_path:
            return abs_path

    # MEDIA_URL
    media_url = (getattr(settings, "MEDIA_URL", "/media/") or "/media/").rstrip("/") + "/"
    if uri.startswith(media_url):
        media_root = Path(getattr(settings, "MEDIA_ROOT", "") or "")
        relpath = uri[len(media_url):].lstrip("/")
        p = media_root / relpath
        if p.exists():
            return str(p.resolve())

    return uri  # fallback (xhtml2pdf tentera)


# =========================================================
# QR CODE
# =========================================================
def _make_qr_png(text: str, out: Path) -> bool:
    out.parent.mkdir(parents=True, exist_ok=True)

    try:
        import qrcode  # type: ignore
        img = qrcode.make(text)
        img.save(str(out))
        return out.exists()
    except Exception:
        pass

    try:
        import segno  # type: ignore
        qr = segno.make(text, error="M")
        qr.save(str(out), kind="png", scale=6, border=2)
        return out.exists()
    except Exception:
        return False


def _qr_abs_for_order(order: Order) -> str:
    qr_dir = Path(
        getattr(
            settings,
            "PDF_QR_DIR",
            Path(getattr(settings, "MEDIA_ROOT", "")) / "invoices" / "qr",
        )
    )

    ref = (order.reference or str(order.uuid)).strip()
    out = qr_dir / f"order-{order.uuid}.png"

    if not out.exists():
        _make_qr_png(ref, out)

    return str(out.resolve()) if out.exists() else ""


# =========================================================
# SECURITY
# =========================================================
def _get_order_for_user_or_404(request, uuid) -> Order:
    """
    Accès sécurisé :
    - staff : OK
    - propriétaire : OK
    - sinon : 404 (no leak)
    """
    order = get_object_or_404(Order, uuid=uuid)

    if request.user.is_staff:
        return order

    if order.user_id and order.user_id == request.user.id:
        return order

    raise Http404


# =========================================================
# PDF CONTEXT
# =========================================================
def _pdf_context(order: Order, doc_type: str) -> dict[str, Any]:
    assets_sub = getattr(settings, "PDF_ASSETS_SUBDIR", "pdf")

    return {
        "doc_type": doc_type,
        "order": order,
        "now": timezone.now(),
        "PROJECT_NAME": getattr(settings, "PROJECT_NAME", "SOGENTIS"),

        "COMPANY_ADDRESS": getattr(settings, "COMPANY_ADDRESS", ""),
        "COMPANY_LEGAL": getattr(settings, "COMPANY_LEGAL", ""),
        "COMPANY_PHONE": getattr(settings, "COMPANY_PHONE", ""),
        "COMPANY_EMAIL": getattr(settings, "COMPANY_EMAIL", ""),
        "COMPANY_WEBSITE": getattr(settings, "COMPANY_WEBSITE", ""),

        # chemins ABS (xhtml2pdf + link_callback)
        "LOGO_ABS": _static_abs(f"{assets_sub}/logo.png"),
        "STAMP_ABS": _static_abs(f"{assets_sub}/stamp.png"),
        "SIGN_ABS": _static_abs(f"{assets_sub}/signature.png"),
        "QR_ABS": _qr_abs_for_order(order),
    }


# =========================================================
# PDF RENDERING
# =========================================================
def _render_pdf(
    request,
    template: str,
    context: dict[str, Any],
    filename: str,
) -> HttpResponse:
    """
    - xhtml2pdf absent → HTML téléchargeable
    - PDF erreur → HTML fallback
    - sinon → PDF
    """
    html = render(request, template, context).content.decode("utf-8")

    if not HAS_PDF:
        resp = HttpResponse(html, content_type="text/html; charset=utf-8")
        resp["Content-Disposition"] = f'attachment; filename="{filename}.html"'
        return resp

    result = BytesIO()
    pdf = pisa.CreatePDF(
        src=html,
        dest=result,
        encoding="utf-8",
        link_callback=_link_callback,  # 🔑
    )

    if pdf.err:
        resp = HttpResponse(html, content_type="text/html; charset=utf-8")
        resp["Content-Disposition"] = f'attachment; filename="{filename}.html"'
        return resp

    resp = HttpResponse(result.getvalue(), content_type="application/pdf")
    resp["Content-Disposition"] = f'attachment; filename="{filename}.pdf"'
    return resp


# =========================================================
# VIEWS
# =========================================================
@login_required
def proforma_download_view(request, uuid):
    """
    Proforma :
    - accessible avant paiement
    - accessible après (archivage)
    - Date limite : 2 semaines (14 jours)
    """
    order = _get_order_for_user_or_404(request, uuid)

    context = _pdf_context(order, doc_type="proforma")
    context["due_date"] = timezone.localdate() + timedelta(days=14)

    filename = f"proforma-{order.reference or order.uuid}"

    return _render_pdf(
        request,
        "economic/ecommerce/invoices/proforma.html",
        context,
        filename,
    )


@login_required
def invoice_download_view(request, uuid):
    """
    Facture :
    - uniquement si payée
    """
    order = _get_order_for_user_or_404(request, uuid)

    if not getattr(order, "is_paid", False):
        messages.error(
            request,
            _("La facture est disponible uniquement après paiement. Téléchargez la proforma."),
        )
        return redirect(
            "economic:ecommerce:proforma_download",
            uuid=order.uuid,
        )

    context = _pdf_context(order, doc_type="invoice")
    filename = f"invoice-{order.reference or order.uuid}"

    return _render_pdf(
        request,
        "economic/ecommerce/invoices/invoice.html",
        context,
        filename,
    )







# # economic/ecommerce/views/invoice.py
# from __future__ import annotations

# from io import BytesIO
# from pathlib import Path
# from typing import Any

# from django.conf import settings
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.http import Http404, HttpResponse
# from django.shortcuts import get_object_or_404, redirect, render
# from django.utils import timezone
# from django.utils.translation import gettext as _

# from ..models.order import Order

# # =========================================================
# # PDF availability
# # =========================================================
# try:
#     from xhtml2pdf import pisa  # type: ignore
#     HAS_PDF = True
# except Exception:
#     HAS_PDF = False


# # =========================================================
# # STATIC & MEDIA resolution (xhtml2pdf compatible)
# # =========================================================
# def _static_abs(rel: str) -> str:
#     """
#     Retourne un chemin absolu vers un fichier statique.
#     - prod: STATIC_ROOT
#     - dev: STATICFILES_DIRS
#     """
#     rel = str(rel).lstrip("/").replace("\\", "/")

#     static_root = Path(getattr(settings, "STATIC_ROOT", "") or "")
#     if static_root:
#         p = static_root / rel
#         if p.exists():
#             return str(p.resolve())

#     for d in getattr(settings, "STATICFILES_DIRS", []) or []:
#         p = Path(d) / rel
#         if p.exists():
#             return str(p.resolve())

#     return ""


# def _link_callback(uri: str, rel: str | None = None) -> str:
#     """
#     Convertit les URLs (static/media) en chemins locaux
#     requis par xhtml2pdf.
#     """
#     uri = (uri or "").replace("\\", "/").strip()

#     # Chemin absolu déjà valide
#     try:
#         p = Path(uri)
#         if p.is_absolute() and p.exists():
#             return str(p)
#     except Exception:
#         pass

#     # STATIC_URL
#     static_url = (getattr(settings, "STATIC_URL", "/static/") or "/static/").rstrip("/") + "/"
#     if uri.startswith(static_url):
#         abs_path = _static_abs(uri[len(static_url):])
#         if abs_path:
#             return abs_path

#     # MEDIA_URL
#     media_url = (getattr(settings, "MEDIA_URL", "/media/") or "/media/").rstrip("/") + "/"
#     if uri.startswith(media_url):
#         media_root = Path(getattr(settings, "MEDIA_ROOT", "") or "")
#         relpath = uri[len(media_url):].lstrip("/")
#         p = media_root / relpath
#         if p.exists():
#             return str(p.resolve())

#     return uri  # fallback (xhtml2pdf tentera)


# # =========================================================
# # QR CODE
# # =========================================================
# def _make_qr_png(text: str, out: Path) -> bool:
#     out.parent.mkdir(parents=True, exist_ok=True)

#     try:
#         import qrcode  # type: ignore
#         img = qrcode.make(text)
#         img.save(str(out))
#         return out.exists()
#     except Exception:
#         pass

#     try:
#         import segno  # type: ignore
#         qr = segno.make(text, error="M")
#         qr.save(str(out), kind="png", scale=6, border=2)
#         return out.exists()
#     except Exception:
#         return False


# def _qr_abs_for_order(order: Order) -> str:
#     qr_dir = Path(
#         getattr(
#             settings,
#             "PDF_QR_DIR",
#             Path(getattr(settings, "MEDIA_ROOT", "")) / "invoices" / "qr",
#         )
#     )

#     ref = (order.reference or str(order.uuid)).strip()
#     out = qr_dir / f"order-{order.uuid}.png"

#     if not out.exists():
#         _make_qr_png(ref, out)

#     return str(out.resolve()) if out.exists() else ""


# # =========================================================
# # SECURITY
# # =========================================================
# def _get_order_for_user_or_404(request, uuid) -> Order:
#     """
#     Accès sécurisé :
#     - staff : OK
#     - propriétaire : OK
#     - sinon : 404 (no leak)
#     """
#     order = get_object_or_404(Order, uuid=uuid)

#     if request.user.is_staff:
#         return order

#     if order.user_id and order.user_id == request.user.id:
#         return order

#     raise Http404


# # =========================================================
# # PDF CONTEXT
# # =========================================================
# def _pdf_context(order: Order, doc_type: str) -> dict[str, Any]:
#     assets_sub = getattr(settings, "PDF_ASSETS_SUBDIR", "pdf")

#     return {
#         "doc_type": doc_type,
#         "order": order,
#         "now": timezone.now(),
#         "PROJECT_NAME": getattr(settings, "PROJECT_NAME", "SOGENTIS"),

#         "COMPANY_ADDRESS": getattr(settings, "COMPANY_ADDRESS", ""),
#         "COMPANY_LEGAL": getattr(settings, "COMPANY_LEGAL", ""),
#         "COMPANY_PHONE": getattr(settings, "COMPANY_PHONE", ""),
#         "COMPANY_EMAIL": getattr(settings, "COMPANY_EMAIL", ""),
#         "COMPANY_WEBSITE": getattr(settings, "COMPANY_WEBSITE", ""),

#         # chemins ABS (xhtml2pdf + link_callback)
#         "LOGO_ABS": _static_abs(f"{assets_sub}/logo.png"),
#         "STAMP_ABS": _static_abs(f"{assets_sub}/stamp.png"),
#         "SIGN_ABS": _static_abs(f"{assets_sub}/signature.png"),
#         "QR_ABS": _qr_abs_for_order(order),
#     }


# # =========================================================
# # PDF RENDERING
# # =========================================================
# def _render_pdf(
#     request,
#     template: str,
#     context: dict[str, Any],
#     filename: str,
# ) -> HttpResponse:
#     """
#     - xhtml2pdf absent → HTML téléchargeable
#     - PDF erreur → HTML fallback
#     - sinon → PDF
#     """
#     html = render(request, template, context).content.decode("utf-8")

#     if not HAS_PDF:
#         resp = HttpResponse(html, content_type="text/html; charset=utf-8")
#         resp["Content-Disposition"] = f'attachment; filename="{filename}.html"'
#         return resp

#     result = BytesIO()
#     pdf = pisa.CreatePDF(
#         src=html,
#         dest=result,
#         encoding="utf-8",
#         link_callback=_link_callback,  # 🔑
#     )

#     if pdf.err:
#         resp = HttpResponse(html, content_type="text/html; charset=utf-8")
#         resp["Content-Disposition"] = f'attachment; filename="{filename}.html"'
#         return resp

#     resp = HttpResponse(result.getvalue(), content_type="application/pdf")
#     resp["Content-Disposition"] = f'attachment; filename="{filename}.pdf"'
#     return resp


# # =========================================================
# # VIEWS
# # =========================================================
# @login_required
# def proforma_download_view(request, uuid):
#     """
#     Proforma :
#     - accessible avant paiement
#     - accessible après (archivage)
#     """
#     order = _get_order_for_user_or_404(request, uuid)

#     context = _pdf_context(order, doc_type="proforma")
#     filename = f"proforma-{order.reference or order.uuid}"

#     return _render_pdf(
#         request,
#         "economic/ecommerce/invoices/proforma.html",
#         context,
#         filename,
#     )


# @login_required
# def invoice_download_view(request, uuid):
#     """
#     Facture :
#     - uniquement si payée
#     """
#     order = _get_order_for_user_or_404(request, uuid)

#     if not getattr(order, "is_paid", False):
#         messages.error(
#             request,
#             _("La facture est disponible uniquement après paiement. Téléchargez la proforma."),
#         )
#         return redirect(
#             "economic:ecommerce:proforma_download",
#             uuid=order.uuid,
#         )

#     context = _pdf_context(order, doc_type="invoice")
#     filename = f"invoice-{order.reference or order.uuid}"

#     return _render_pdf(
#         request,
#         "economic/ecommerce/invoices/invoice.html",
#         context,
#         filename,
#     )






# # economic/ecommerce/views/invoice.py
# from __future__ import annotations

# from io import BytesIO
# from pathlib import Path
# from typing import Any

# from django.conf import settings
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.http import Http404, HttpResponse
# from django.shortcuts import get_object_or_404, redirect, render
# from django.utils import timezone
# from django.utils.translation import gettext as _

# from ..models.order import Order

# try:
#     from xhtml2pdf import pisa  # type: ignore
#     HAS_PDF = True
# except Exception:
#     HAS_PDF = False


# # =========================================================
# #  STATIC ABSOLUTE PATH (for xhtml2pdf)
# # =========================================================
# def _static_abs(rel: str) -> str:
#     """
#     Retourne un chemin ABSOLU vers un fichier statique.
#     - prod: STATIC_ROOT/...
#     - dev: premier STATICFILES_DIRS où le fichier existe
#     """
#     rel = str(rel).lstrip("/").replace("\\", "/")

#     # 1) prod (collectstatic)
#     static_root = Path(getattr(settings, "STATIC_ROOT", "") or "")
#     if str(static_root):
#         p = static_root / rel
#         if p.exists():
#             return str(p.resolve())

#     # 2) dev (STATICFILES_DIRS)
#     for d in getattr(settings, "STATICFILES_DIRS", []) or []:
#         base = Path(d)
#         p = base / rel
#         if p.exists():
#             return str(p.resolve())

#     return ""


# def _link_callback(uri: str, rel: str | None = None) -> str:
#     """
#     xhtml2pdf: convertit les URI (static/media) en chemins locaux.
#     """
#     uri = (uri or "").replace("\\", "/").strip()

#     # Déjà un chemin absolu existant
#     try:
#         p = Path(uri)
#         if p.is_absolute() and p.exists():
#             return str(p)
#     except Exception:
#         pass

#     # STATIC_URL
#     static_url = (getattr(settings, "STATIC_URL", "/static/") or "/static/").rstrip("/") + "/"
#     if uri.startswith(static_url):
#         relpath = uri[len(static_url):]
#         abs_path = _static_abs(relpath)
#         if abs_path:
#             return abs_path

#     # MEDIA_URL
#     media_url = (getattr(settings, "MEDIA_URL", "/media/") or "/media/").rstrip("/") + "/"
#     if uri.startswith(media_url):
#         relpath = uri[len(media_url):].lstrip("/")
#         media_root = Path(getattr(settings, "MEDIA_ROOT", "") or "")
#         if str(media_root):
#             p = (media_root / relpath)
#             if p.exists():
#                 return str(p.resolve())

#     # sinon: renvoyer tel quel (xhtml2pdf tentera)
#     return uri


# # =========================================================
# #  QR (PNG) generation
# # =========================================================
# def _make_qr_png(text: str, out_path: Path) -> bool:
#     """
#     Génère un QR PNG. Tente qrcode, sinon segno.
#     """
#     out_path.parent.mkdir(parents=True, exist_ok=True)

#     # qrcode (si installé)
#     try:
#         import qrcode  # type: ignore

#         img = qrcode.make(text)
#         img.save(str(out_path))
#         return out_path.exists()
#     except Exception:
#         pass

#     # segno (si installé)
#     try:
#         import segno  # type: ignore

#         qr = segno.make(text, error="M")
#         qr.save(str(out_path), kind="png", scale=6, border=2)
#         return out_path.exists()
#     except Exception:
#         return False


# def _qr_abs_for_order(order: Order) -> str:
#     """
#     QR code = reference (ou uuid) — pratique pour vérifier la doc.
#     """
#     qr_dir: Path = getattr(
#         settings,
#         "PDF_QR_DIR",
#         Path(getattr(settings, "MEDIA_ROOT", "")) / "invoices" / "qr",
#     )

#     ref = (order.reference or str(order.uuid)).strip()
#     qr_text = ref

#     out = qr_dir / f"order-{order.uuid}.png"
#     if not out.exists():
#         _make_qr_png(qr_text, out)

#     return str(out.resolve()) if out.exists() else ""


# # =========================================================
# #  ACCESS CONTROL
# # =========================================================
# def _get_order_for_user_or_404(request, uuid) -> Order:
#     """
#     Sécurise l'accès:
#     - owner: OK
#     - staff: OK
#     - sinon: 404 (ne pas leak)
#     """
#     order = get_object_or_404(Order, uuid=uuid)

#     if request.user.is_staff:
#         return order

#     if getattr(order, "user_id", None) and order.user_id == request.user.id:
#         return order

#     raise Http404


# # =========================================================
# #  PDF rendering
# # =========================================================
# def _render_pdf(template_name: str, context: dict[str, Any], filename: str, request) -> HttpResponse:
#     """
#     - Si xhtml2pdf absent => retourne HTML téléchargeable
#     - Sinon => PDF (xhtml2pdf) + link_callback pour images
#     """
#     if not HAS_PDF:
#         html = render(request, template_name, context).content
#         resp = HttpResponse(html, content_type="text/html; charset=utf-8")
#         resp["Content-Disposition"] = f'attachment; filename="{filename}.html"'
#         return resp

#     html_str = render(request, template_name, context).content.decode("utf-8")
#     result = BytesIO()

#     # ✅ link_callback indispensable pour images
#     pdf = pisa.CreatePDF(
#         src=html_str,
#         dest=result,
#         link_callback=_link_callback,  # type: ignore
#         encoding="utf-8",
#     )

#     if pdf.err:
#         # fallback HTML si erreur PDF
#         resp = HttpResponse(html_str, content_type="text/html; charset=utf-8")
#         resp["Content-Disposition"] = f'attachment; filename="{filename}.html"'
#         return resp

#     resp = HttpResponse(result.getvalue(), content_type="application/pdf")
#     resp["Content-Disposition"] = f'attachment; filename="{filename}.pdf"'
#     return resp


# # =========================================================
# #  VIEWS
# # =========================================================
# @login_required
# def proforma_download_view(request, uuid):
#     """
#     ✅ Proforma: disponible AVANT paiement
#     (pending) — mais autorisée aussi si shipped/completed (utile archivage).
#     """
#     order = _get_order_for_user_or_404(request, uuid)

#     assets_sub = getattr(settings, "PDF_ASSETS_SUBDIR", "pdf")
#     context = {
#         "doc_type": "proforma",
#         "order": order,
#         "now": timezone.now(),
#         "PROJECT_NAME": getattr(settings, "PROJECT_NAME", "SOGENTIS"),

#         "COMPANY_ADDRESS": getattr(settings, "COMPANY_ADDRESS", ""),
#         "COMPANY_LEGAL": getattr(settings, "COMPANY_LEGAL", ""),
#         "COMPANY_PHONE": getattr(settings, "COMPANY_PHONE", ""),
#         "COMPANY_EMAIL": getattr(settings, "COMPANY_EMAIL", ""),
#         "COMPANY_WEBSITE": getattr(settings, "COMPANY_WEBSITE", ""),

#         "LOGO_ABS": _static_abs(f"{assets_sub}/logo.png"),
#         "STAMP_ABS": _static_abs(f"{assets_sub}/stamp.png"),
#         "SIGN_ABS": _static_abs(f"{assets_sub}/signature.png"),
#         "QR_ABS": _qr_abs_for_order(order),
#     }

#     filename = f"proforma-{order.reference or order.uuid}"
#     return _render_pdf("economic/ecommerce/invoices/proforma_premium.html", context, filename, request=request)


# @login_required
# def invoice_download_view(request, uuid):
#     """
#     ✅ Facture: disponible UNIQUEMENT après paiement
#     (order.is_paid=True)
#     """
#     order = _get_order_for_user_or_404(request, uuid)

#     if not getattr(order, "is_paid", False):
#         messages.error(
#             request,
#             _("La facture est disponible uniquement après paiement. Téléchargez la proforma."),
#         )
#         return redirect("economic:ecommerce:proforma_download", uuid=order.uuid)

#     assets_sub = getattr(settings, "PDF_ASSETS_SUBDIR", "pdf")
#     context = {
#         "doc_type": "invoice",
#         "order": order,
#         "now": timezone.now(),
#         "PROJECT_NAME": getattr(settings, "PROJECT_NAME", "SOGENTIS"),

#         "COMPANY_ADDRESS": getattr(settings, "COMPANY_ADDRESS", ""),
#         "COMPANY_LEGAL": getattr(settings, "COMPANY_LEGAL", ""),
#         "COMPANY_PHONE": getattr(settings, "COMPANY_PHONE", ""),
#         "COMPANY_EMAIL": getattr(settings, "COMPANY_EMAIL", ""),
#         "COMPANY_WEBSITE": getattr(settings, "COMPANY_WEBSITE", ""),

#         "LOGO_ABS": _static_abs(f"{assets_sub}/logo.png"),
#         "STAMP_ABS": _static_abs(f"{assets_sub}/stamp.png"),
#         "SIGN_ABS": _static_abs(f"{assets_sub}/signature.png"),
#         "QR_ABS": _qr_abs_for_order(order),
#     }

#     filename = f"invoice-{order.reference or order.uuid}"
#     return _render_pdf("economic/ecommerce/invoices/invoice_premium.html", context, filename, request=request)







# # economic/ecommerce/views/invoice.py
# from __future__ import annotations

# from io import BytesIO
# from pathlib import Path

# from django.conf import settings
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.http import HttpResponse
# from django.shortcuts import get_object_or_404, redirect, render
# from django.utils.translation import gettext as _

# from ..models.order import Order

# try:
#     from xhtml2pdf import pisa
#     HAS_PDF = True
# except Exception:
#     HAS_PDF = False


# def _static_abs(rel: str) -> str:
#     """
#     Retourne un chemin ABSOLU vers un fichier statique.
#     - prod: STATIC_ROOT/...
#     - dev: premier STATICFILES_DIRS où le fichier existe
#     """
#     rel = str(rel).lstrip("/").replace("\\", "/")

#     # 1) prod
#     static_root = Path(getattr(settings, "STATIC_ROOT", "") or "")
#     if static_root:
#         p = (static_root / rel)
#         if p.exists():
#             return str(p.resolve())

#     # 2) dev
#     for d in getattr(settings, "STATICFILES_DIRS", []) or []:
#         base = Path(d)
#         p = base / rel
#         if p.exists():
#             return str(p.resolve())

#     return ""


# def _make_qr_png(text: str, out_path: Path) -> bool:
#     """
#     Génère un QR PNG. Tente qrcode, sinon segno.
#     """
#     out_path.parent.mkdir(parents=True, exist_ok=True)

#     # qrcode (si installé)
#     try:
#         import qrcode  # type: ignore

#         img = qrcode.make(text)
#         img.save(str(out_path))
#         return out_path.exists()
#     except Exception:
#         pass

#     # segno (si installé)
#     try:
#         import segno  # type: ignore

#         qr = segno.make(text, error="M")
#         qr.save(str(out_path), kind="png", scale=6, border=2)
#         return out_path.exists()
#     except Exception:
#         return False


# def _qr_abs_for_order(order: Order) -> str:
#     """
#     QR code = référence / uuid + URL (si besoin)
#     """
#     qr_dir: Path = getattr(settings, "PDF_QR_DIR", Path(settings.MEDIA_ROOT) / "invoices" / "qr")
#     ref = (order.reference or str(order.uuid)).strip()
#     qr_text = ref

#     out = qr_dir / f"order-{order.uuid}.png"
#     if not out.exists():
#         _make_qr_png(qr_text, out)

#     return str(out.resolve()) if out.exists() else ""


# def _render_pdf(template_name: str, context: dict, filename: str, request=None) -> HttpResponse:
#     if not HAS_PDF:
#         html = render(request, template_name, context).content
#         resp = HttpResponse(html, content_type="text/html; charset=utf-8")
#         resp["Content-Disposition"] = f'attachment; filename="{filename}.html"'
#         return resp

#     html_str = render(request, template_name, context).content.decode("utf-8")
#     result = BytesIO()
#     pisa.CreatePDF(html_str, dest=result)

#     resp = HttpResponse(result.getvalue(), content_type="application/pdf")
#     resp["Content-Disposition"] = f'attachment; filename="{filename}.pdf"'
#     return resp

# # economic/ecommerce/views/invoice.py (suite)
# @login_required
# def proforma_download_view(request, uuid):
#     order = get_object_or_404(Order, uuid=uuid, user=request.user)

#     assets_sub = getattr(settings, "PDF_ASSETS_SUBDIR", "pdf")
#     context = {
#         "order": order,
#         "PROJECT_NAME": getattr(settings, "PROJECT_NAME", "SOGENTIS"),

#         "COMPANY_ADDRESS": getattr(settings, "COMPANY_ADDRESS", ""),
#         "COMPANY_LEGAL": getattr(settings, "COMPANY_LEGAL", ""),
#         "COMPANY_PHONE": getattr(settings, "COMPANY_PHONE", ""),
#         "COMPANY_EMAIL": getattr(settings, "COMPANY_EMAIL", ""),
#         "COMPANY_WEBSITE": getattr(settings, "COMPANY_WEBSITE", ""),

#         "LOGO_ABS": _static_abs(f"{assets_sub}/logo.png"),
#         "STAMP_ABS": _static_abs(f"{assets_sub}/stamp.png"),
#         "SIGN_ABS": _static_abs(f"{assets_sub}/signature.png"),
#         "QR_ABS": _qr_abs_for_order(order),
#     }

#     filename = f"proforma-{order.reference or order.uuid}"
#     return _render_pdf("economic/ecommerce/invoices/proforma_premium.html", context, filename, request=request)


# @login_required
# def invoice_download_view(request, uuid):
#     order = get_object_or_404(Order, uuid=uuid, user=request.user)

#     if not getattr(order, "is_paid", False):
#         messages.error(request, _("La facture est disponible uniquement après paiement. Téléchargez la proforma."))
#         return redirect("economic:ecommerce:proforma_download", uuid=order.uuid)

#     assets_sub = getattr(settings, "PDF_ASSETS_SUBDIR", "pdf")
#     context = {
#         "order": order,
#         "PROJECT_NAME": getattr(settings, "PROJECT_NAME", "SOGENTIS"),

#         "COMPANY_ADDRESS": getattr(settings, "COMPANY_ADDRESS", ""),
#         "COMPANY_LEGAL": getattr(settings, "COMPANY_LEGAL", ""),
#         "COMPANY_PHONE": getattr(settings, "COMPANY_PHONE", ""),
#         "COMPANY_EMAIL": getattr(settings, "COMPANY_EMAIL", ""),
#         "COMPANY_WEBSITE": getattr(settings, "COMPANY_WEBSITE", ""),

#         "LOGO_ABS": _static_abs(f"{assets_sub}/logo.png"),
#         "STAMP_ABS": _static_abs(f"{assets_sub}/stamp.png"),
#         "SIGN_ABS": _static_abs(f"{assets_sub}/signature.png"),
#         "QR_ABS": _qr_abs_for_order(order),
#     }

#     filename = f"invoice-{order.reference or order.uuid}"
#     return _render_pdf("economic/ecommerce/invoices/invoice_premium.html", context, filename, request=request)




# # economic/ecommerce/views/invoice.py
# from __future__ import annotations

# from io import BytesIO
# from pathlib import Path

# from django.conf import settings
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.http import HttpResponse
# from django.shortcuts import get_object_or_404, redirect, render
# from django.utils.translation import gettext as _

# from ..models.order import Order

# try:
#     from xhtml2pdf import pisa
#     HAS_PDF = True
# except Exception:
#     HAS_PDF = False


# def _abs_static_file(rel_path: str) -> str:
#     """
#     xhtml2pdf lit mieux les images via file:///ABS_PATH.
#     On pointe vers /static/... ou vers un dossier assets si tu en as un.
#     """
#     # option 1: dossier assets dédié (recommandé)
#     # ex: <project_root>/static_assets/pdf/logo.png
#     base = getattr(settings, "PDF_ASSETS_DIR", "")
#     if base:
#         p = Path(base) / rel_path
#         return str(p.resolve())

#     # option 2: STATIC_ROOT (si collectstatic)
#     static_root = getattr(settings, "STATIC_ROOT", "") or ""
#     if static_root:
#         p = Path(static_root) / rel_path
#         return str(p.resolve())

#     return ""


# def _render_pdf_from_template(request, template_name: str, context: dict, filename: str) -> HttpResponse:
#     # fallback HTML si xhtml2pdf absent
#     if not HAS_PDF:
#       html = render(request, template_name, context).content
#       resp = HttpResponse(html, content_type="text/html; charset=utf-8")
#       resp["Content-Disposition"] = f'attachment; filename="{filename}.html"'
#       return resp

#     html_str = render(request, template_name, context).content.decode("utf-8")
#     result = BytesIO()
#     pisa.CreatePDF(html_str, dest=result)

#     resp = HttpResponse(result.getvalue(), content_type="application/pdf")
#     resp["Content-Disposition"] = f'attachment; filename="{filename}.pdf"'
#     return resp


# @login_required
# def proforma_download_view(request, uuid):
#     """
#     ✅ Proforma = AVANT paiement (toujours autorisée si commande appartient à l'utilisateur)
#     """
#     order = get_object_or_404(Order, uuid=uuid, user=request.user)

#     context = {
#         "order": order,
#         "PROJECT_NAME": getattr(settings, "PROJECT_NAME", "SOGENTIS"),
#         "COMPANY_ADDRESS": getattr(settings, "COMPANY_ADDRESS", ""),
#         # Mets tes fichiers ici (paths relatifs à STATIC_ROOT ou PDF_ASSETS_DIR)
#         "LOGO_ABS": _abs_static_file("global/img/logo.png"),
#         "STAMP_ABS": _abs_static_file("global/img/stamp.png"),
#         "SIGN_ABS": _abs_static_file("global/img/signature.png"),
#     }

#     filename = f"proforma-{order.reference or order.uuid}"
#     return _render_pdf_from_template(request, "economic/ecommerce/invoices/proforma.html", context, filename)


# @login_required
# def invoice_download_view(request, uuid):
#     """
#     ✅ Facture = APRES paiement seulement
#     """
#     order = get_object_or_404(Order, uuid=uuid, user=request.user)

#     if not getattr(order, "is_paid", False):
#         messages.error(request, _("La facture est disponible uniquement après paiement. Téléchargez la proforma en attendant."))
#         return redirect("economic:ecommerce:proforma_download", uuid=order.uuid)

#     context = {
#         "order": order,
#         "PROJECT_NAME": getattr(settings, "PROJECT_NAME", "SOGENTIS"),
#         "COMPANY_ADDRESS": getattr(settings, "COMPANY_ADDRESS", ""),
#         "LOGO_ABS": _abs_static_file("global/img/logo.png"),
#         "STAMP_ABS": _abs_static_file("global/img/stamp.png"),
#         "SIGN_ABS": _abs_static_file("global/img/signature.png"),
#     }

#     filename = f"invoice-{order.reference or order.uuid}"
#     return _render_pdf_from_template(request, "economic/ecommerce/invoices/invoice.html", context, filename)





# # economic/ecommerce/views/invoice.py
# from __future__ import annotations

# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import get_object_or_404, redirect
# from django.utils.translation import gettext as _

# from ..models.order import Order
# from ..services.pdf_utils import render_pdf, static_abs_path


# def _invoice_assets_context() -> dict:
#     return {
#         "LOGO_ABS": static_abs_path("global/branding/logo.png"),
#         "STAMP_ABS": static_abs_path("global/branding/stamp.png"),
#         "SIGN_ABS": static_abs_path("global/branding/signature.png"),
#     }


# @login_required
# def proforma_download_view(request, uuid):
#     order = get_object_or_404(Order, uuid=uuid, user=request.user)

#     ctx = {"order": order}
#     ctx.update(_invoice_assets_context())

#     return render_pdf(
#         "economic/ecommerce/invoices/proforma.html",
#         ctx,
#         filename=f"proforma-{order.reference or order.uuid}",
#     )


# @login_required
# def invoice_download_view(request, uuid):
#     order = get_object_or_404(Order, uuid=uuid, user=request.user)

#     if not getattr(order, "is_paid", False):
#         messages.error(request, _("La facture est disponible uniquement après paiement."))
#         return redirect("economic:ecommerce:order_detail", uuid=order.uuid)

#     ctx = {"order": order}
#     ctx.update(_invoice_assets_context())

#     return render_pdf(
#         "economic/ecommerce/invoices/invoice.html",
#         ctx,
#         filename=f"invoice-{order.reference or order.uuid}",
#     )





# # economic/ecommerce/views/invoice.py
# from __future__ import annotations

# from io import BytesIO

# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.http import HttpResponse
# from django.shortcuts import get_object_or_404, render, redirect
# from django.utils.translation import gettext as _

# from ..models.order import Order

# try:
#     from xhtml2pdf import pisa
#     HAS_PDF = True
# except ImportError:
#     HAS_PDF = False


# def _render_pdf_from_template(request, template_name: str, context: dict, filename: str) -> HttpResponse:
#     if not HAS_PDF:
#         html = render(request, template_name, context).content
#         resp = HttpResponse(html, content_type="text/html; charset=utf-8")
#         resp["Content-Disposition"] = f'attachment; filename="{filename}.html"'
#         return resp

#     html_str = render(request, template_name, context).content.decode("utf-8")
#     result = BytesIO()
#     pisa.CreatePDF(html_str, dest=result)

#     resp = HttpResponse(result.getvalue(), content_type="application/pdf")
#     resp["Content-Disposition"] = f'attachment; filename="{filename}.pdf"'
#     return resp


# @login_required
# def proforma_download_view(request, uuid):
#     """
#     Proforma: avant paiement.
#     """
#     order = get_object_or_404(Order, uuid=uuid, user=request.user)
#     return _render_pdf_from_template(
#         request,
#         "economic/ecommerce/invoices/proforma.html",
#         {"order": order},
#         filename=f"proforma-{order.reference or order.uuid}",
#     )


# @login_required
# def invoice_download_view(request, uuid):
#     """
#     Facture: après paiement.
#     """
#     order = get_object_or_404(Order, uuid=uuid, user=request.user)
#     if not getattr(order, "is_paid", False):
#         messages.error(request, _("La facture est disponible uniquement après paiement."))
#         return redirect("economic:ecommerce:order_detail", uuid=order.uuid)

#     return _render_pdf_from_template(
#         request,
#         "economic/ecommerce/invoices/invoice.html",
#         {"order": order},
#         filename=f"invoice-{order.reference or order.uuid}",
#     )





# # economic/ecommerce/views/invoice.py
# from __future__ import annotations

# from io import BytesIO

# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.http import HttpResponse
# from django.shortcuts import get_object_or_404, redirect, render
# from django.utils.translation import gettext as _

# from ..models.order import Order

# try:
#     from xhtml2pdf import pisa
#     HAS_PDF = True
# except ImportError:
#     HAS_PDF = False


# def _render_pdf_from_template(request, template_name: str, context: dict, filename: str) -> HttpResponse:
#     if not HAS_PDF:
#         html = render(request, template_name, context).content
#         resp = HttpResponse(html, content_type="text/html; charset=utf-8")
#         resp["Content-Disposition"] = f'attachment; filename="{filename}.html"'
#         return resp

#     html_str = render(request, template_name, context).content.decode("utf-8")
#     result = BytesIO()
#     pisa.CreatePDF(html_str, dest=result)
#     resp = HttpResponse(result.getvalue(), content_type="application/pdf")
#     resp["Content-Disposition"] = f'attachment; filename="{filename}.pdf"'
#     return resp


# @login_required
# def proforma_download_view(request, uuid):
#     order = get_object_or_404(Order, uuid=uuid, user=request.user)
#     context = {"order": order}
#     return _render_pdf_from_template(
#         request,
#         "economic/ecommerce/invoices/proforma.html",
#         context,
#         filename=f"proforma-{order.reference or order.uuid}",
#     )


# @login_required
# def invoice_download_view(request, uuid):
#     order = get_object_or_404(Order, uuid=uuid, user=request.user)

#     # ✅ Facture seulement après paiement
#     if not getattr(order, "is_paid", False):
#         messages.info(request, _("Commande non payée : téléchargement de la proforma."))
#         return redirect("economic:ecommerce:proforma_download", uuid=order.uuid)

#     context = {"order": order}
#     return _render_pdf_from_template(
#         request,
#         "economic/ecommerce/invoices/invoice.html",
#         context,
#         filename=f"invoice-{order.reference or order.uuid}",
#     )







# # economic/ecommerce/views/invoice.py
# from __future__ import annotations

# from io import BytesIO

# from django.contrib.auth.decorators import login_required
# from django.http import HttpResponse
# from django.shortcuts import get_object_or_404, render

# from ..models.order import Order

# try:
#     from xhtml2pdf import pisa  # type: ignore
#     HAS_PDF = True
# except Exception:
#     HAS_PDF = False


# @login_required
# def invoice_download_view(request, uuid):
#     """
#     URL:
#       path("invoices/<uuid:uuid>/download/", invoice_download_view, name="invoice_download")

#     Note: par défaut on protège (commande du user).
#     Optionnel: autoriser staff.
#     """
#     qs = Order.objects.filter(uuid=uuid)
#     if not request.user.is_staff:
#         qs = qs.filter(user=request.user)

#     order = get_object_or_404(qs)
#     context = {"order": order}

#     # Fallback HTML si xhtml2pdf pas installé
#     if not HAS_PDF:
#         html = render(request, "economic/ecommerce/invoices/invoice.html", context).content
#         resp = HttpResponse(html, content_type="text/html; charset=utf-8")
#         resp["Content-Disposition"] = f'attachment; filename="invoice-{order.uuid}.html"'
#         return resp

#     html_str = render(request, "economic/ecommerce/invoices/invoice.html", context).content.decode("utf-8")
#     result = BytesIO()
#     pisa.CreatePDF(html_str, dest=result)

#     resp = HttpResponse(result.getvalue(), content_type="application/pdf")
#     resp["Content-Disposition"] = f'attachment; filename="invoice-{order.uuid}.pdf"'
#     return resp






# # economic/ecommerce/views/invoice.py
# from io import BytesIO

# from django.contrib.auth.decorators import login_required
# from django.http import HttpResponse
# from django.shortcuts import get_object_or_404, render

# from ..models.order import Order

# try:
#     from xhtml2pdf import pisa
#     HAS_PDF = True
# except ImportError:
#     HAS_PDF = False


# @login_required
# def invoice_download_view(request, uuid):
#     """
#     URL:
#       path("invoices/<uuid:uuid>/download/", invoice_download_view, name="invoice_download")
#     """
#     order = get_object_or_404(Order, uuid=uuid, user=request.user)
#     context = {"order": order}

#     if not HAS_PDF:
#         html = render(request, "economic/ecommerce/invoices/invoice.html", context).content
#         resp = HttpResponse(html, content_type="text/html; charset=utf-8")
#         resp["Content-Disposition"] = f'attachment; filename="invoice-{order.uuid}.html"'
#         return resp

#     html_str = render(request, "economic/ecommerce/invoices/invoice.html", context).content.decode("utf-8")
#     result = BytesIO()
#     pisa.CreatePDF(html_str, dest=result)

#     resp = HttpResponse(result.getvalue(), content_type="application/pdf")
#     resp["Content-Disposition"] = f'attachment; filename="invoice-{order.uuid}.pdf"'
#     return resp






# from django.contrib.auth.decorators import login_required
# from django.shortcuts import get_object_or_404
# from django.http import FileResponse

# from ..models.invoice import Invoice


# @login_required
# def invoice_download_view(request, uuid):
#     invoice = get_object_or_404(
#         Invoice,
#         uuid=uuid,
#         order__user=request.user,
#     )
#     return FileResponse(
#         invoice.file.open("rb"),
#         as_attachment=True,
#         filename=invoice.file.name,
#     )
