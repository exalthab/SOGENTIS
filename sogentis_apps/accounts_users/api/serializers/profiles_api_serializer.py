# accounts_users/api/serializers/profiles_api_serializer.py
from rest_framework import serializers

from accounts_users.models.users_economic_profile import UserProfile
from accounts_users.models.user_role import UserRole


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = ["id", "name", "description"]


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer API du PROFIL UTILISATEUR CENTRAL
    (Client / Vendor / Company)
    """

    role = RoleSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()
    country_of_residence = serializers.CharField(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "first_name",
            "last_name",
            "full_name",
            "phone",
            "country_of_residence",
            "economic_role",
            "status",
            "role",
        ]

    def get_full_name(self, obj):
        return f"{obj.last_name or ''} {obj.first_name or ''}".strip()





# # accounts_users/api/serializers/profiles_api_serializer.py
# from rest_framework import serializers

# from accounts_users.models.users_profile import UserProfile
# from accounts_users.models.role import UserRole


# class RoleSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserRole
#         fields = ["id", "name", "description"]


# class UserProfileSerializer(serializers.ModelSerializer):
#     """
#     Serializer API du profil utilisateur
#     Aligné strictement avec le modèle UserProfile réel
#     """

#     role = RoleSerializer(read_only=True)
#     full_name = serializers.SerializerMethodField()
#     country_of_residence = serializers.CharField(read_only=True)

#     class Meta:
#         model = UserProfile
#         fields = [
#             "last_name",
#             "phone",
#             "country_of_residence",
#             "message",
#             "judicial_record",
#             "role",
#         ]

#     def get_full_name(self, obj):
#         return f"{obj.last_name or ''} {obj.first_name or ''}".strip()






# # accounts_users/api/serializers/profiles_api_serializer.py
# from rest_framework import serializers
# from accounts_users.models.users_profile import UserProfile
# from accounts_users.models.role import UserRole

# class RoleSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserRole
#         fields = ['id', 'name', 'description']


# class UserProfileSerializer(serializers.ModelSerializer):
#     role = RoleSerializer(read_only=True)

#     class Meta:
#         model = UserProfile
#         fields = ['full_name', 'phone', 'country', 'message', 'judicial_record', 'role']
