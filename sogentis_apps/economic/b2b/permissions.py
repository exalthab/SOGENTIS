# economic/b2b/permissions.py

def is_vendor(user):
    return user.is_authenticated and hasattr(user, "vendor_profile")


def is_verified_vendor(user):
    return (
        is_vendor(user)
        and getattr(user.vendor_profile, "is_verified", False)
    )


def is_b2b_user(user):
    return user.is_authenticated and hasattr(user, "company_user")


def is_b2b_admin(user):
    return (
        is_b2b_user(user)
        and getattr(user.company_user, "is_admin", False)
    )
