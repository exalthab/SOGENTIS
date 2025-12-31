# dashboard/context_processors/dashboard_context.py

from dashboard.permissions import is_vendor, is_b2b_user

def dashboard_info(request):
    """
    Informations globales injectées dans tous les templates dashboard
    """
    if not request.user.is_authenticated:
        return {}

    return {
        "dashboard_user": request.user,
        "dashboard_notifications": 0,  # placeholder (à brancher plus tard)
    }


def dashboard_roles(request):
    """
    Rôles utiles pour afficher dynamiquement le sidebar / menus
    """
    if not request.user.is_authenticated:
        return {
            "is_vendor": bool,
            "is_b2b_user": bool,
        }

    user = request.user

    return {
        "is_vendor": is_vendor(user),
        "is_b2b_user": is_b2b_user(user),
    }


# # dashboard/context_processors/dashboard_context.py
# def dashboard_info(request):
#     if request.user.is_authenticated:
#         return {
#             "dashboard_user": request.user,
#             "dashboard_notifications": 3,  # Exemples à adapter
#         }
#     return {}
