# economic/formations/views/my_dashboard.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from ..models import Enrollment, Certificate, CourseSession


@login_required
def my_dashboard_view(request):
    enrollments = (
        Enrollment.objects.filter(user=request.user)
        .exclude(status=Enrollment.Status.CANCELLED)
        .select_related("course", "course__category")
        .order_by("-enrolled_at")
    )

    active_count = enrollments.filter(status=Enrollment.Status.ACTIVE).count()
    pending_count = enrollments.filter(status=Enrollment.Status.PENDING).count()
    completed_count = enrollments.filter(status=Enrollment.Status.COMPLETED).count()

    certs = (
        Certificate.objects.filter(enrollment__user=request.user, revoked=False)
        .select_related("enrollment", "course")
        .order_by("-issued_at")[:6]
    )

    course_ids = enrollments.values_list("course_id", flat=True)
    now = timezone.now()

    sessions = (
        CourseSession.objects.filter(course_id__in=course_ids, is_active=True)
        .exclude(status=CourseSession.Status.CANCELLED)
        .filter(end_at__gte=now)
        .select_related("course")
        .order_by("start_at")[:10]
    )

    return render(request, "economic/formations/learner/dashboard.html", {
        "enrollments": enrollments[:8],
        "active_count": active_count,
        "pending_count": pending_count,
        "completed_count": completed_count,
        "certificates": certs,
        "sessions": sessions,
    })





# # economic/formations/views/my_dashboard.py
# from __future__ import annotations

# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
# from django.utils import timezone
# from django.db.models import Q

# from ..models import Enrollment, Certificate, CourseSession


# @login_required
# def my_dashboard_view(request):
#     enrollments = (
#         Enrollment.objects.filter(user=request.user)
#         .exclude(status=Enrollment.Status.CANCELLED)
#         .select_related("course", "course__category")
#         .order_by("-enrolled_at")
#     )

#     active_count = enrollments.filter(status=Enrollment.Status.ACTIVE).count()
#     pending_count = enrollments.filter(status=Enrollment.Status.PENDING).count()
#     completed_count = enrollments.filter(status=Enrollment.Status.COMPLETED).count()

#     certs = (
#         Certificate.objects.filter(enrollment__user=request.user, revoked=False)
#         .select_related("enrollment", "course")
#         .order_by("-issued_at")[:6]
#     )

#     course_ids = enrollments.values_list("course_id", flat=True)
#     now = timezone.now()

#     sessions = (
#         CourseSession.objects.filter(course_id__in=course_ids, is_active=True)
#         .filter(Q(end_at__gte=now) | Q(end_at__isnull=True))
#         .select_related("course")
#         .order_by("start_at")[:10]
#     )

#     return render(
#         request,
#         "economic/formations/learner/dashboard.html",
#         {
#             "enrollments": enrollments[:8],
#             "active_count": active_count,
#             "pending_count": pending_count,
#             "completed_count": completed_count,
#             "certificates": certs,
#             "sessions": sessions,
#         },
#     )





# # economic/formations/views/my_dashboard.py
# from __future__ import annotations

# from datetime import timedelta

# from django.contrib.auth.decorators import login_required
# from django.db.models import Q
# from django.shortcuts import render
# from django.utils import timezone

# from ..models import Enrollment, Certificate, CourseSession


# def _has_field(model, field_name: str) -> bool:
#     try:
#         model._meta.get_field(field_name)
#         return True
#     except Exception:
#         return False


# @login_required
# def my_dashboard_view(request):
#     now = timezone.now()

#     enrollments = Enrollment.objects.filter(user=request.user).select_related("course", "course__category")

#     if _has_field(Enrollment, "status") and hasattr(Enrollment, "Status"):
#         enrollments = enrollments.exclude(status=Enrollment.Status.CANCELLED)

#     enrollments = enrollments.order_by("-enrolled_at" if _has_field(Enrollment, "enrolled_at") else "-created_at")

#     # Counts
#     active_count = 0
#     pending_count = 0
#     completed_count = 0
#     if _has_field(Enrollment, "status") and hasattr(Enrollment, "Status"):
#         active_count = enrollments.filter(status=Enrollment.Status.ACTIVE).count()
#         pending_count = enrollments.filter(status=Enrollment.Status.PENDING).count()
#         completed_count = enrollments.filter(status=Enrollment.Status.COMPLETED).count()
#     else:
#         if _has_field(Enrollment, "completed"):
#             completed_count = enrollments.filter(completed=True).count()
#             active_count = max(enrollments.count() - completed_count, 0)

#     # Certificates
#     certs = Certificate.objects.filter(enrollment__user=request.user).select_related("enrollment", "course").order_by("-issued_at")
#     if _has_field(Certificate, "revoked"):
#         certs = certs.filter(revoked=False)
#     certs = certs[:6]

#     # Upcoming sessions
#     course_ids = enrollments.values_list("course_id", flat=True).distinct()

#     sess_qs = CourseSession.objects.filter(course_id__in=course_ids).select_related("course")

#     if _has_field(CourseSession, "is_active"):
#         sess_qs = sess_qs.filter(is_active=True)

#     if _has_field(CourseSession, "status"):
#         sess_qs = sess_qs.exclude(status__in=["CANCELLED", "cancelled"])

#     # Fenêtre temps
#     time_filter = (Q(end_at__gte=now) | Q(end_at__isnull=True)) & Q(start_at__lte=now + timedelta(days=90))
#     sessions = sess_qs.filter(time_filter).order_by("start_at", "id")[:10]

#     return render(
#         request,
#         "economic/formations/learner/dashboard.html",
#         {
#             "enrollments": enrollments[:8],
#             "active_count": active_count,
#             "pending_count": pending_count,
#             "completed_count": completed_count,
#             "certificates": certs,
#             "sessions": sessions,
#             "now": now,
#         },
#     )





# # economic/formations/views/my_dashboard.py
# from __future__ import annotations

# from django.contrib.auth.decorators import login_required
# from django.db.models import Q
# from django.shortcuts import render
# from django.utils import timezone

# from ..models import Enrollment, Certificate, CourseSession


# def _has_field(model, field_name: str) -> bool:
#     try:
#         model._meta.get_field(field_name)
#         return True
#     except Exception:
#         return False


# @login_required
# def my_dashboard_view(request):
#     now = timezone.now()

#     enrollments = Enrollment.objects.filter(user=request.user).select_related("course", "course__category")

#     # Exclure annulés si champ status existe
#     if _has_field(Enrollment, "status") and hasattr(Enrollment, "Status"):
#         enrollments = enrollments.exclude(status=Enrollment.Status.CANCELLED)

#     # Ordering safe
#     if _has_field(Enrollment, "enrolled_at"):
#         enrollments = enrollments.order_by("-enrolled_at")
#     else:
#         enrollments = enrollments.order_by("-created_at")

#     # Counts (compat status + legacy completed)
#     active_count = 0
#     pending_count = 0
#     completed_count = 0

#     if _has_field(Enrollment, "status") and hasattr(Enrollment, "Status"):
#         active_count = enrollments.filter(status=Enrollment.Status.ACTIVE).count()
#         pending_count = enrollments.filter(status=Enrollment.Status.PENDING).count()
#         completed_count = enrollments.filter(status=Enrollment.Status.COMPLETED).count()
#     else:
#         # fallback legacy
#         if _has_field(Enrollment, "completed"):
#             completed_count = enrollments.filter(completed=True).count()
#             active_count = max(enrollments.count() - completed_count, 0)

#     # Certificates
#     certs = Certificate.objects.filter(enrollment__user=request.user).select_related("enrollment", "course").order_by("-issued_at")
#     if _has_field(Certificate, "revoked"):
#         certs = certs.filter(revoked=False)
#     certs = certs[:6]

#     # Sessions à venir pour les cours de l’utilisateur
#     course_ids = enrollments.values_list("course_id", flat=True).distinct()

#     sess_qs = CourseSession.objects.filter(course_id__in=course_ids).select_related("course")

#     # Actif / statut si présents
#     if _has_field(CourseSession, "is_active"):
#         sess_qs = sess_qs.filter(is_active=True)

#     if _has_field(CourseSession, "status"):
#         # Exclure CANCELLED si tu utilises ce status
#         sess_qs = sess_qs.exclude(status__in=["CANCELLED", "cancelled"])

#     # Fenêtre temps : end_at >= now OU end_at NULL (session “ouverte”)
#     # + start_at pas trop loin (optionnel)
#     time_filter = Q(end_at__gte=now) | Q(end_at__isnull=True)
#     if _has_field(CourseSession, "start_at"):
#         sess_qs = sess_qs.filter(start_at__gte=now - timezone.timedelta(days=1))  # tolérance 24h

#     sessions = (
#         sess_qs.filter(time_filter)
#         .order_by("start_at", "id")[:10]
#     )

#     return render(
#         request,
#         "economic/formations/learner/dashboard.html",
#         {
#             "enrollments": enrollments[:8],
#             "active_count": active_count,
#             "pending_count": pending_count,
#             "completed_count": completed_count,
#             "certificates": certs,
#             "sessions": sessions,
#             "now": now,
#         },
#     )






# # economic/formations/views/my_dashboard.py
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
# from django.utils import timezone

# from ..models import Enrollment, Certificate, CourseSession


# @login_required
# def my_dashboard_view(request):
#     enrollments = (
#         Enrollment.objects.filter(user=request.user)
#         .exclude(status=Enrollment.Status.CANCELLED)
#         .select_related("course", "course__category")
#         .order_by("-enrolled_at")
#     )

#     active_count = enrollments.filter(status=Enrollment.Status.ACTIVE).count()
#     pending_count = enrollments.filter(status=Enrollment.Status.PENDING).count()
#     completed_count = enrollments.filter(status=Enrollment.Status.COMPLETED).count()

#     certs = (
#         Certificate.objects.filter(enrollment__user=request.user, revoked=False)
#         .select_related("enrollment", "course")
#         .order_by("-issued_at")[:6]
#     )

#     course_ids = enrollments.values_list("course_id", flat=True)
#     now = timezone.now()
#     sessions = (
#         CourseSession.objects.filter(course_id__in=course_ids, is_cancelled=False, ends_at__gte=now)
#         .select_related("course")
#         .order_by("starts_at")[:10]
#     )

#     return render(request, "economic/formations/learner/dashboard.html", {
#         "enrollments": enrollments[:8],
#         "active_count": active_count,
#         "pending_count": pending_count,
#         "completed_count": completed_count,
#         "certificates": certs,
#         "sessions": sessions,
#     })
