# accounts_users/web/serializers/web_serializer.py 21/12/2025 error

from accounts_users.models.users_economic_profile import UserProfile
def profile_to_dict(profile: UserProfile) -> dict:
    """
    Sérialisation simple du profil utilisateur (WEB).
    Alignée strictement avec le modèle UserProfile réel.
    """
    if not profile:
        return {}

    full_name = f"{profile.last_name or ''} {profile.first_name or ''}".strip()

    return {
        "full_name": full_name or None,
        "phone": profile.phone,
        "country_of_residence": profile.country_of_residence,
        "role": profile.role.name if profile.role else None,
        "message": profile.message,
    }


def user_to_dict(user) -> dict:
    """
    Sérialisation simple de l'utilisateur (WEB).
    """
    profile = getattr(user, "userprofile", None)

    return {
        "email": user.email,
        "is_staff": user.is_staff,
        "profile": profile_to_dict(profile),
    }







# # accounts_users/web/serializers/web_serializer.py November 2025
# from accounts_users.models.users_profile import UserProfile

# def profile_to_dict(profile: UserProfile) -> dict:
#     return {
#         "full_name": profile.full_name,
#         "phone": profile.phone,
#         "country": profile.country,
#         "role": profile.role.name if profile.role else None,
#         "message": profile.message,
#     }


# def user_to_dict(user) -> dict:
#     profile = getattr(user, 'userprofile', None)
#     return {
#         "email": user.email,
#         "is_staff": user.is_staff,
#         "profile": profile_to_dict(profile) if profile else {},
#     }








