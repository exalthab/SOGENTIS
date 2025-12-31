from rest_framework import serializers
from accounts_users.models.social.social_profile import SocialProfile


class SocialProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = SocialProfile
        fields = [
            "first_name",
            "last_name",
            "full_name",
            "phone",
            "membership_role",
            "judicial_record",
            "motivation",
            "availability",
            "skills",
            "is_validated",
        ]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()
