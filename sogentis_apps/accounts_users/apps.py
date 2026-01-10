# accounts_users/apps.py
from django.apps import AppConfig


class AccountsUsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts_users"

    def ready(self):
        # Import signals (enregistrement des receivers)
        from .signals import profile_validation_signals  # noqa
        from .signals import membership_role_signals    # noqa







# # accounts_users/apps.py
# from django.apps import AppConfig


# class AccountsUsersConfig(AppConfig):
#     default_auto_field = "django.db.models.BigAutoField"
#     name = "accounts_users"

#     def ready(self):
#         # Import signals
#         from .signals import profile_validation_signals  # noqa





# # accounts_users/apps.py
# from django.apps import AppConfig


# class AccountsUsersConfig(AppConfig):
#     name = "accounts_users"

#     def ready(self):
#         import accounts_users.signals.profile_status_signal








# from django.apps import AppConfig

# class AccountsUsersConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'accounts_users'

#     def ready(self):
#         # import accounts_users.signals
#         import accounts_users.signals.users_signals
