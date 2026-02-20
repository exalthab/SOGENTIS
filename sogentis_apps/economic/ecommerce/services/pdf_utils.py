# economic/ecommerce/services/pdf_utils.py
from __future__ import annotations

from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template

try:
    from xhtml2pdf import pisa
    HAS_PDF = True
except Exception:
    HAS_PDF = False


def static_abs_path(static_relative_path: str) -> str:
    """
    Transforme un chemin 'global/branding/logo.png' en chemin absolu fichier
    compatible xhtml2pdf.
    """
    base_dirs = []

    # STATICFILES_DIRS (dev)
    for p in getattr(settings, "STATICFILES_DIRS", []) or []:
        base_dirs.append(Path(p))

    # STATIC_ROOT (prod collectstatic)
    static_root = getattr(settings, "STATIC_ROOT", None)
    if static_root:
        base_dirs.append(Path(static_root))

    rel = Path(static_relative_path)

    for base in base_dirs:
        cand = (base / rel).resolve()
        if cand.exists():
            return str(cand)

    # fallback: renvoie un chemin "probable" (au pire l'image ne s'affichera pas)
    if static_root:
        return str((Path(static_root) / rel).resolve())
    if base_dirs:
        return str((base_dirs[0] / rel).resolve())
    return str(rel)


def render_pdf(template_name: str, context: dict, filename: str) -> HttpResponse:
    """
    Rend un PDF via xhtml2pdf. Fallback HTML si xhtml2pdf absent.
    """
    tpl = get_template(template_name)
    html = tpl.render(context)

    if not HAS_PDF:
        resp = HttpResponse(html, content_type="text/html; charset=utf-8")
        resp["Content-Disposition"] = f'attachment; filename="{filename}.html"'
        return resp

    out = BytesIO()
    pisa.CreatePDF(html, dest=out)

    resp = HttpResponse(out.getvalue(), content_type="application/pdf")
    resp["Content-Disposition"] = f'attachment; filename="{filename}.pdf"'
    return resp
