# economic/b2b/services/permissions.py
from functools import wraps

from django.http import Http404
from django.contrib.auth.decorators import login_required

from ..models import CompanyUser


def get_company_user_or_403(user) -> CompanyUser:
    try:
        cu = CompanyUser.objects.select_related("company").get(user=user, is_active=True, company__is_active=True)
    except CompanyUser.DoesNotExist:
        raise Http404("Accès B2B non autorisé.")
    return cu


def company_user_required(view_func):
    @login_required
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        request.company_user = get_company_user_or_403(request.user)
        return view_func(request, *args, **kwargs)

    return _wrapped
