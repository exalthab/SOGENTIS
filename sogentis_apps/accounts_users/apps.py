# accounts_users/apps.py
from django.apps import AppConfig


class AccountsUsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts_users"
    verbose_name = "Accounts & Users"

    def ready(self):
        # Auto-activation admin/superuser
        from .signals import admin_profile_signals  # noqa
        # Import signals (enregistrement des receivers)
        # ⚠️ chaque import doit être safe pour éviter crash prod si module optionnel
        from .signals import membership_role_signals  # noqa
        from .signals import user_validation_signals  # noqa

        try:
            from .signals import profile_validation_signals  # noqa
        except Exception:
            pass

        try:
            from .signals import profile_status_signal  # noqa
        except Exception:
            pass

        try:
            from .signals import users_signals  # noqa
        except Exception:
            pass




# # accounts_users/apps.py
# from django.apps import AppConfig


# class AccountsUsersConfig(AppConfig):
#     default_auto_field = "django.db.models.BigAutoField"
#     name = "accounts_users"

#     def ready(self):
#         # Import signals (enregistrement des receivers)
#         from .signals import profile_validation_signals  # noqa
#         from .signals import membership_role_signals    # noqa
#         from .signals import user_validation_signals  # noqa







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
