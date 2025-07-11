def dashboard_info(request):
    if request.user.is_authenticated:
        return {
            "dashboard_user": request.user,
            "dashboard_notifications": 3,  # Exemples à adapter
        }
    return {}
