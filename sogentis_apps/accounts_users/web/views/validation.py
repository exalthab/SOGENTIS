# accounts_users/web/views/validation.py
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_GET

User = get_user_model()

@require_GET
def check_email_availability(request):
    email = (request.GET.get("email") or "").strip().lower()
    if not email:
        return JsonResponse({"available": False})

    exists = User.objects.filter(email__iexact=email).exists()
    return JsonResponse({"available": not exists})
