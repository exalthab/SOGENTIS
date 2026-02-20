# accounting/services/balance.py
from __future__ import annotations

from datetime import date
from typing import Any, Dict, Optional

from accounting.selectors.report_queries import compute_balance_sheet, compute_profit_loss, compute_trial_balance


def trial_balance_service(*, pole: str = "", company_code: str = "", start: Optional[date] = None, end: Optional[date] = None) -> Dict[str, Any]:
    return compute_trial_balance(pole=pole, company_code=company_code, start=start, end=end)


def profit_loss_service(*, pole: str = "", company_code: str = "", start: Optional[date] = None, end: Optional[date] = None) -> Dict[str, Any]:
    return compute_profit_loss(pole=pole, company_code=company_code, start=start, end=end)


def balance_sheet_service(*, pole: str = "", company_code: str = "", as_of: date) -> Dict[str, Any]:
    return compute_balance_sheet(pole=pole, company_code=company_code, as_of=as_of)
