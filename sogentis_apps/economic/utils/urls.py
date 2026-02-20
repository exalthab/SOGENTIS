# economic/utils/urls.py
from __future__ import annotations

from typing import Any

from django.urls import NoReverseMatch, reverse


def safe_reverse(viewname: str, default: str = "#", *args: Any, **kwargs: Any) -> str:
    """
    reverse() sans crash: renvoie `default` si la route n'existe pas.
    Supporte args/kwargs pour les urls dynamiques.
    """
    try:
        return reverse(viewname, args=args, kwargs=kwargs)
    except NoReverseMatch:
        return default
