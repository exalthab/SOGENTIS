# dashboard/urls/accounting.py
from __future__ import annotations

from django.urls import path

from dashboard.views.accounting import accounts, journal_entries, index, journal, reports

app_name = "accounting"

urlpatterns = [
    path("", index.accounting_index_view, name="index"),

    # Chart of Accounts
    path("accounts/", accounts.accounts_list_view, name="accounts"),
    path("accounts/<int:pk>/", accounts.account_detail_view, name="account_detail"),

    # Journal
    path("journal/", journal.journal_list_view, name="journal"),
    path("journal/<int:pk>/", journal.journal_detail_view, name="journal_detail"),

    # Entries
    path("entries/", journal_entries.entries_list_view, name="entries"),
    path("entries/<int:pk>/", journal_entries.entry_detail_view, name="entry_detail"),

    # Reports home (UI dashboard)
    path("reports/", reports.reports_home_view, name="reports"),

    # Shortcuts -> accounting app (source unique)
    path("reports/trial-balance/", reports.trial_balance_view, name="trial_balance"),
    path("reports/profit-loss/", reports.profit_loss_view, name="profit_loss"),
    path("reports/balance-sheet/", reports.balance_sheet_view, name="balance_sheet"),
    path("reports/cash-flow/", reports.cash_flow_view, name="cash_flow"),
]





# # dashboard/urls/accounting.py
# from __future__ import annotations

# from django.urls import path

# from dashboard.views.accounting import accounts, journal_entries, index, journal, reports

# app_name = "accounting"

# urlpatterns = [
#     path("", index.accounting_index_view, name="index"),

#     # Chart of Accounts
#     path("accounts/", accounts.accounts_list_view, name="accounts"),
#     path("accounts/<int:pk>/", accounts.account_detail_view, name="account_detail"),

#     # Journal (si modèles dispo)
#     path("journal/", journal.journal_list_view, name="journal"),
#     path("journal/<int:pk>/", journal.journal_detail_view, name="journal_detail"),

#     # Entries
#     path("entries/", journal_entries.entries_list_view, name="entries"),
#     path("entries/<int:pk>/", journal_entries.entry_detail_view, name="entry_detail"),

#   # Reports (QuickBooks-like)
#     path("reports/", reports.reports_home_view, name="reports"),
#     path("reports/trial-balance/", reports.trial_balance_view, name="trial_balance"),
#     path("reports/profit-loss/", reports.profit_loss_view, name="profit_loss"),
#     path("reports/balance-sheet/", reports.balance_sheet_view, name="balance_sheet"),
# ]
