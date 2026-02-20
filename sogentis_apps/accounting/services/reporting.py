# accounting/services/reporting.py
from __future__ import annotations

from datetime import date
from typing import Any, Dict, Optional

from accounting.services.trial_balance import balance_sheet_service, profit_loss_service, trial_balance_service


def run_trial_balance(*, pole: str = "", company_code: str = "", start: Optional[date] = None, end: Optional[date] = None) -> Dict[str, Any]:
    return trial_balance_service(pole=pole, company_code=company_code, start=start, end=end)


def run_profit_loss(*, pole: str = "", company_code: str = "", start: Optional[date] = None, end: Optional[date] = None) -> Dict[str, Any]:
    return profit_loss_service(pole=pole, company_code=company_code, start=start, end=end)


def run_balance_sheet(*, pole: str = "", company_code: str = "", as_of: date) -> Dict[str, Any]:
    return balance_sheet_service(pole=pole, company_code=company_code, as_of=as_of)
