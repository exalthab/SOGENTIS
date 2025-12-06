# from .dashboard_note import DashboardNote
# dashboard/models/__init__.py

from .dashboard_note import DashboardNote
from .activity_log import UserActivityLog

__all__ = [
    "DashboardNote",
    "UserActivityLog",
]
