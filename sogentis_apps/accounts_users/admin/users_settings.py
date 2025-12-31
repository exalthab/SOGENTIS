# accounts_users/admin/users_settings.py
from django.contrib import admin

from accounts_users.admin.admin_base import BaseAdmin
from accounts_users.models.users_settings import UserSettings


@admin.register(UserSettings)
class UserSettingsAdmin(BaseAdmin):
    list_display = (
        "user",
        "language",
        "dark_mode",
        "receive_newsletter",
        "created_at_display",
        "updated_at_display",
    )

    list_filter = (
        "language",
        "dark_mode",
        "receive_newsletter",
    )

    search_fields = (
        "user__email",
        "user__username",
    )



# # accounts_users/admin/settings_admin.py
# from django.contrib import admin
# from django.utils.translation import gettext_lazy as _

# from accounts_users.admin.admin_base import BaseAdmin
# from accounts_users.models.users_settings import UserSettings


# @admin.register(UserSettings)
# class UserSettingsAdmin(BaseAdmin):
#     """
#     Paramètres utilisateur (langue, thème, notifications).
#     """

#     list_display = (
#         "user",
#         "language",
#         "theme",
#         "receive_notifications",
#         "created_at_display",
#         "updated_at_display",
#     )

#     list_filter = (
#         "language",
#         "theme",
#         "receive_notifications",
#     )

#     search_fields = (
#         "user__email",
#         "user__username",
#     )





# # accounts_users/admin/settings_admin.py

# from django.contrib import admin
# from accounts_users.models.users_settings import UserSettings


# @admin.register(UserSettings)
# class UserSettingsAdmin(admin.ModelAdmin):
#     list_display = ('user', 'language', 'receive_notifications', 'theme')
#     list_filter = ('language', 'receive_notifications', 'theme')
#     search_fields = ('user__email', 'user__username')
