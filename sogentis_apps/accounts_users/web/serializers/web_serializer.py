from accounts_users.models.users_profile import UserProfile

def profile_to_dict(profile: UserProfile) -> dict:
    return {
        "full_name": profile.full_name,
        "phone": profile.phone,
        "country": profile.country,
        "role": profile.role.name if profile.role else None,
        "message": profile.message,
    }


def user_to_dict(user) -> dict:
    profile = getattr(user, 'userprofile', None)
    return {
        "email": user.email,
        "is_staff": user.is_staff,
        "profile": profile_to_dict(profile) if profile else {},
    }
