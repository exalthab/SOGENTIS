# accounting/urls.py
from __future__ import annotations

from django.urls import path

from accounting.views import dashboard, reports

app_name = "accounting"

urlpatterns = [
    # Dashboard (Accounting hub)
    path("", dashboard.accounting_dashboard_view, name="dashboard"),
    path("balance-sheet/", dashboard.balance_sheet_view, name="balance_sheet"),
    path("trial-balance/", dashboard.trial_balance_shortcut_view, name="trial_balance_shortcut"),
    path("profit-loss/", dashboard.profit_loss_shortcut_view, name="profit_loss_shortcut"),

    # Reports (source unique)
    path("reports/trial-balance/", reports.trial_balance_view, name="trial_balance"),
    path("reports/ledger/<int:account_id>/", reports.ledger_view, name="ledger"),
    path("reports/trial-balance.csv", reports.trial_balance_csv_view, name="trial_balance_csv"),

    path("reports/balance-sheet/", reports.balance_sheet_report_view, name="report_balance_sheet"),
    path("reports/income-statement/", reports.income_statement_report_view, name="report_income_statement"),
    path("reports/cash-flow/", reports.cash_flow_report_view, name="report_cash_flow"),

    path("cash-flow/", dashboard.cash_flow_shortcut_view, name="cash_flow_shortcut"),

]






# # accounting/urls.py
# from __future__ import annotations

# from django.urls import path

# from accounting.views import reports

# app_name = "accounting"

# urlpatterns = [
#     # Reports
#     path("reports/trial-balance/", reports.trial_balance_view, name="trial_balance"),
#     path("reports/ledger/<int:account_id>/", reports.ledger_view, name="ledger"),
#     path("reports/trial-balance.csv", reports.trial_balance_csv_view, name="trial_balance_csv"),
# ]
