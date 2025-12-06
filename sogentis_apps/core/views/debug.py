#core/views/debug.py
from django.http import JsonResponse
from django.utils import translation
from django.conf import settings
from django.views.decorators.http import require_GET

@require_GET
def lang_debug(request):
    session_key = getattr(translation, "LANGUAGE_SESSION_KEY", "django_language")
    return JsonResponse({
        "active_language": translation.get_language(),
        "request_LANGUAGE_CODE": getattr(request, "LANGUAGE_CODE", None),
        "session_language": request.session.get(session_key),
        "cookie_language": request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME),
    })