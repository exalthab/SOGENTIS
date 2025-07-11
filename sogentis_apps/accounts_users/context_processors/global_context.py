def user_roles(request):
    if request.user.is_authenticated:
        return {"user_role": getattr(request.user, "role", "Invité")}
    return {"user_role": "Anonyme"}
