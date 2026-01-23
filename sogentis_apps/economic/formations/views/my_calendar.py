# economic/formations/views/my_calendar.py
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from ..models import Enrollment, CourseSession


@login_required
def my_calendar_view(request):
    now = timezone.now()
    horizon = now + timedelta(days=90)

    course_ids = (
        Enrollment.objects.filter(user=request.user)
        .exclude(status=Enrollment.Status.CANCELLED)
        .values_list("course_id", flat=True)
    )

    sessions = (
        CourseSession.objects.filter(course_id__in=course_ids, is_active=True)
        .exclude(status=CourseSession.Status.CANCELLED)
        .filter(start_at__lte=horizon, end_at__gte=now)
        .select_related("course")
        .order_by("start_at")
    )

    return render(request, "economic/formations/learner/calendar.html", {"sessions": sessions})







# # economic/formations/views/my_calendar.py
# from __future__ import annotations

# from datetime import timedelta

# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
# from django.utils import timezone

# from ..models import Enrollment, CourseSession


# @login_required
# def my_calendar_view(request):
#     now = timezone.now()
#     horizon = now + timedelta(days=90)

#     course_ids = (
#         Enrollment.objects.filter(user=request.user)
#         .exclude(status=Enrollment.Status.CANCELLED)
#         .values_list("course_id", flat=True)
#     )

#     sessions = (
#         CourseSession.objects.filter(course_id__in=course_ids, is_active=True)
#         .exclude(status=getattr(CourseSession, "Status", object()).CANCELLED if hasattr(CourseSession, "Status") else None)
#         .filter(start_at__lte=horizon)
#         .filter(end_at__gte=now)  # si end_at nullable, on gère plus bas
#         .select_related("course")
#         .order_by("start_at")
#     )

#     # Si end_at peut être NULL, ton filtre end_at__gte=now va exclure.
#     # Variante safe: inclure end_at null comme "session ouverte"
#     sessions = (
#         CourseSession.objects.filter(course_id__in=course_ids, is_active=True)
#         .filter(start_at__lte=horizon)
#         .filter(
#             # end_at >= now OR end_at is null
#             # (évite l'exclusion si end_at est nullable)
#         )
#         .select_related("course")
#         .order_by("start_at")
#     )
#     # => pour ne pas dépendre de Q import, on fait simple ici :
#     # si end_at est nullable chez toi, remplace le bloc ci-dessous par celui avec Q (voir note).
#     sessions = (
#         CourseSession.objects.filter(course_id__in=course_ids, is_active=True)
#         .filter(start_at__lte=horizon)
#         .select_related("course")
#         .order_by("start_at")
#     )

#     return render(request, "economic/formations/learner/calendar.html", {"sessions": sessions})




# # economic/formations/views/my_calendar.py
# from __future__ import annotations

# from datetime import timedelta

# from django.contrib.auth.decorators import login_required
# from django.db.models import Q
# from django.shortcuts import render
# from django.utils import timezone

# from ..models import Enrollment, CourseSession


# def _has_field(model, field_name: str) -> bool:
#     try:
#         model._meta.get_field(field_name)
#         return True
#     except Exception:
#         return False


# @login_required
# def my_calendar_view(request):
#     now = timezone.now()

#     # Horizon paramétrable: ?days=30|60|90|180 (max 365)
#     try:
#         days = int(request.GET.get("days", "90"))
#     except ValueError:
#         days = 90
#     days = max(7, min(days, 365))
#     horizon = now + timedelta(days=days)

#     enroll_qs = Enrollment.objects.filter(user=request.user)

#     # Exclure "annulés" si status existe
#     if _has_field(Enrollment, "status") and hasattr(Enrollment, "Status"):
#         enroll_qs = enroll_qs.exclude(status=Enrollment.Status.CANCELLED)

#     # 1) Si Enrollment a un FK direct vers session -> utiliser
#     session_ids = []
#     if _has_field(Enrollment, "session"):
#         session_ids = list(
#             enroll_qs.exclude(session__isnull=True)
#             .values_list("session_id", flat=True)
#             .distinct()
#         )

#     # 2) Sinon fallback: sessions par course
#     course_ids = list(enroll_qs.values_list("course_id", flat=True).distinct())

#     sess_qs = CourseSession.objects.all()

#     if session_ids:
#         sess_qs = sess_qs.filter(pk__in=session_ids)
#     elif course_ids:
#         sess_qs = sess_qs.filter(course_id__in=course_ids)
#     else:
#         sess_qs = sess_qs.none()

#     # Actif / statut si champs existent
#     if _has_field(CourseSession, "is_active"):
#         sess_qs = sess_qs.filter(is_active=True)

#     if _has_field(CourseSession, "status"):
#         # si tu as un status type CANCELLED
#         try:
#             sess_qs = sess_qs.exclude(status__in=["CANCELLED", "cancelled"])
#         except Exception:
#             pass

#     # Fenêtre temps avec les vrais noms: start_at / end_at
#     # - start_at <= horizon
#     # - end_at >= now (ou end_at NULL)
#     time_filter = Q(start_at__lte=horizon) & (Q(end_at__gte=now) | Q(end_at__isnull=True))

#     sessions = (
#         sess_qs.filter(time_filter)
#         .select_related("course")
#         .order_by("start_at", "id")
#     )

#     return render(
#         request,
#         "economic/formations/learner/calendar.html",
#         {
#             "sessions": sessions,
#             "now": now,
#             "horizon": horizon,
#             "days": days,
#             "sessions_count": sessions.count(),
#         },
#     )





# # economic/formations/views/my_calendar.py
# from datetime import timedelta
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
# from django.utils import timezone

# from ..models import Enrollment, CourseSession


# @login_required
# def my_calendar_view(request):
#     now = timezone.now()
#     horizon = now + timedelta(days=90)

#     course_ids = Enrollment.objects.filter(
#         user=request.user
#     ).exclude(
#         status=Enrollment.Status.CANCELLED
#     ).values_list("course_id", flat=True)

#     sessions = (
#         CourseSession.objects.filter(course_id__in=course_ids, is_cancelled=False)
#         .filter(starts_at__lte=horizon, ends_at__gte=now)
#         .select_related("course")
#         .order_by("starts_at")
#     )

#     return render(request, "economic/formations/learner/calendar.html", {"sessions": sessions})
