# economic/b2b/context_processors.py
from __future__ import annotations

from typing import Any


def b2b_context(request) -> dict[str, Any]:
    """
    Injecte un contexte B2B minimal, safe et stable.
    Source de vérité:
      - request.company / request.company_user (posés par company_user_required)
    """
    company = getattr(request, "company", None)
    company_user = getattr(request, "company_user", None)

    return {
        "B2B_COMPANY": company,
        "B2B_COMPANY_ID": getattr(company, "id", None),
        "B2B_COMPANY_USER": company_user,
        "B2B_IS_COMPANY_CONTEXT": bool(company),
    }
