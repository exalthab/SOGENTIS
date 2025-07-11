from rest_framework import serializers
from accounts_users.models.users_profile import UserProfile
from accounts_users.models.role import UserRole

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = ['id', 'name', 'description']


class UserProfileSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['full_name', 'phone', 'country', 'message', 'judicial_record', 'role']
