# payments/services/intent_service.py
from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.contrib.contenttypes.models import ContentType

from payments.models import PaymentIntent


def create_intent(
    *,
    user,
    amount: Decimal,
    currency: str,
    pole: str,
    description: str = "",
    obj: Any | None = None,
    metadata: dict | None = None,
    return_url: str = "",
    cancel_url: str = "",
) -> PaymentIntent:
    ct = ContentType.objects.get_for_model(obj.__class__) if obj else None
    oid = str(getattr(obj, "pk", "")) if obj else ""

    intent = PaymentIntent.objects.create(
        user=user,
        amount=amount,
        currency=(currency or "XOF").upper(),
        pole=pole,
        description=description[:240],
        content_type=ct,
        object_id=oid,
        metadata=metadata or {},
        return_url=return_url or "",
        cancel_url=cancel_url or "",
    )
    return intent
