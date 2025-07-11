from django.core.exceptions import PermissionDenied

def role_required(*allowed_roles):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            user = request.user
            if user.is_authenticated and user.userprofile.role and user.userprofile.role.name in allowed_roles:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied
        return wrapper
    return decorator
