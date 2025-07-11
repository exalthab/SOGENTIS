from django.core.exceptions import PermissionDenied

def user_is_profile_owner(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and str(request.user.id) == kwargs.get("user_id"):
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return wrapper


def user_has_role(*roles):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            profile = getattr(request.user, 'userprofile', None)
            if profile and profile.role and profile.role.name in roles:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied
        return wrapper
    return decorator
