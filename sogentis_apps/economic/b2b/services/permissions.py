# economic/b2b/services/permissions.py
from functools import wraps

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from economic.b2b.models import Company, CompanyUser


def get_company_user_or_403(request, company_id: int) -> CompanyUser:
    """
    Récupère l'appartenance de l'utilisateur à l'entreprise, sinon 403.
    Autorise aussi le owner comme admin implicite.
    """
    company = get_object_or_404(Company, pk=company_id)

    if not request.user.is_authenticated:
        raise PermissionDenied

    # Owner => accès total
    if company.owner_id and company.owner_id == request.user.id:
        cu, _ = CompanyUser.objects.get_or_create(
            user=request.user,
            company=company,
            defaults={"role": CompanyUser.Role.ADMIN, "is_active": True},
        )
        return cu

    cu = CompanyUser.objects.filter(
        user=request.user,
        company=company,
        is_active=True,
    ).first()

    if not cu:
        raise PermissionDenied

    return cu


def company_user_required(view_func=None, *, role: str | None = None):
    """
    Décorateur : exige que request.user soit membre de l'entreprise.
    Si role est fourni: exige au moins ce rôle (admin/staff/viewer).
    """
    def decorator(fn):
        @wraps(fn)
        def _wrapped(request, *args, **kwargs):
            company_id = kwargs.get("company_id")
            if not company_id:
                raise PermissionDenied("company_id manquant dans l'URL.")

            cu = get_company_user_or_403(request, company_id)

            if role:
                allowed = {CompanyUser.Role.ADMIN}
                if role == CompanyUser.Role.STAFF:
                    allowed |= {CompanyUser.Role.STAFF}
                if role == CompanyUser.Role.VIEWER:
                    allowed |= {CompanyUser.Role.VIEWER}

                if cu.role not in allowed:
                    raise PermissionDenied

            request.company_user = cu
            request.company = cu.company
            return fn(request, *args, **kwargs)
        return _wrapped

    return decorator(view_func) if view_func else decorator





# # economic/b2b/services/permissions.py
# from functools import wraps

# from django.http import Http404
# from django.contrib.auth.decorators import login_required

# from ..models import CompanyUser


# def get_company_user_or_403(user) -> CompanyUser:
#     try:
#         cu = CompanyUser.objects.select_related("company").get(user=user, is_active=True, company__is_active=True)
#     except CompanyUser.DoesNotExist:
#         raise Http404("Accès B2B non autorisé.")
#     return cu


# def company_user_required(view_func):
#     @login_required
#     @wraps(view_func)
#     def _wrapped(request, *args, **kwargs):
#         request.company_user = get_company_user_or_403(request.user)
#         return view_func(request, *args, **kwargs)

#     return _wrapped
