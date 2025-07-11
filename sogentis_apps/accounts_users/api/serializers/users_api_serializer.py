from rest_framework import serializers
from django.contrib.auth import get_user_model
from accounts_users.api.serializers.profiles_api_serializer import UserProfileSerializer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(source='userprofile', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'is_active', 'is_staff', 'profile']
