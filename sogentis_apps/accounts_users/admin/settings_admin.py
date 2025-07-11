# accounts_users/admin/settings_admin.py

from django.contrib import admin
from accounts_users.models.users_settings import UserSettings


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'language', 'receive_notifications', 'theme')
    list_filter = ('language', 'receive_notifications', 'theme')
    search_fields = ('user__email', 'user__username')
