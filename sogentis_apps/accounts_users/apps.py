# accounts_users/apps.py
from django.apps import AppConfig

class AccountsUsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts_users'

    def ready(self):
        # import accounts_users.signals
        import accounts_users.signals.users_signals
