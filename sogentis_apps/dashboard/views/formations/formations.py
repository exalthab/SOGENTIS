# dashboard/views/formations/formations.py
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.functions import TruncDay
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from dashboard.views.utils import StatCard, breadcrumb


def _imports():
    """
    Imports safe (ne casse pas le dashboard si formations n'est pas encore migré).
    """
    try:
        from economic.formations.models import Enrollment, Certificate
    except Exception as exc:
        raise Http404(_("Le module Formations n'est pas disponible.")) from exc

    try:
        from economic.formations.models import CourseSession
    except Exception:
        CourseSession = None  # type: ignore

    return Enrollment, Certificate, CourseSession


def _has_status_field(Enrollment) -> bool:
    try:
        Enrollment._meta.get_field("status")
        return True
    except Exception:
        return False


def _status_value(Enrollment, name: str) -> Optional[str]:
    st = getattr(Enrollment, "Status", None)
    return getattr(st, name, None) if st else None


def _status_completed_value(Enrollment) -> Optional[str]:
    return _status_value(Enrollment, "COMPLETED")


def _status_cancelled_value(Enrollment) -> Optional[str]:
    return _status_value(Enrollment, "CANCELLED")


def _enrollment_is_completed(enrollment) -> bool:
    if getattr(enrollment, "completed", False):
        return True
    completed_val = _status_completed_value(enrollment.__class__)
    return bool(completed_val and getattr(enrollment, "status", None) == completed_val)


def _dt_to_ical(dt: datetime) -> str:
    dt_utc = timezone.make_naive(dt.astimezone(timezone.utc), timezone.utc)
    return dt_utc.strftime("%Y%m%dT%H%M%SZ")


def _escape_ical(text: str) -> str:
    return (
        (text or "")
        .replace("\\", "\\\\")
        .replace(";", r"\;")
        .replace(",", r"\,")
        .replace("\n", r"\n")
    )


def _parse_range_days(request, default_days: int = 30) -> int:
    raw = (request.GET.get("range") or str(default_days)).strip()
    if raw in {"7", "30", "90", "180"}:
        return int(raw)
    return default_days


def _safe_iso_datetime(value: Optional[str], fallback: datetime) -> datetime:
    if not value:
        return fallback
    try:
        dt = datetime.fromisoformat(value)
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt)
        return dt
    except Exception:
        return fallback


@login_required
def formations_home_view(request):
    Enrollment, Certificate, CourseSession = _imports()

    # === QS Inscriptions ===
    days = _parse_range_days(request, default_days=30)
    since = timezone.now() - timedelta(days=days)

    qs = Enrollment.objects.filter(user=request.user).select_related("course")

    has_status = _has_status_field(Enrollment)
    cancelled = _status_cancelled_value(Enrollment) if has_status else None
    completed_val = _status_completed_value(Enrollment) if has_status else None

    if cancelled:
        qs = qs.exclude(status=cancelled)

    qs = qs.order_by("-enrolled_at")

    # === Stats fiables ===
    total = qs.count()
    if completed_val:
        completed_count = qs.filter(status=completed_val).count()
    else:
        if hasattr(Enrollment, "completed"):
            completed_count = qs.filter(completed=True).count()
        else:
            completed_count = 0
    active_count = max(total - completed_count, 0)

    # === Dernières inscriptions ===
    enrollments = list(qs[:10])
    course_ids = list(qs.values_list("course_id", flat=True).distinct()[:1500])

    # === Certificats récents ===
    certs = (
        Certificate.objects.filter(enrollment__user=request.user)
        .select_related("course", "enrollment")
        .order_by("-issued_at")[:6]
    )

    # === Sessions à venir ===
    sessions = []
    calendar_enabled = bool(CourseSession)
    if CourseSession and course_ids:
        now = timezone.now()
        sessions = list(
            CourseSession.objects.filter(course_id__in=course_ids, is_cancelled=False, ends_at__gte=now)
            .select_related("course")
            .order_by("starts_at")[:10]
        )

    # === Chart Inscriptions/jour ===
    chart_labels, chart_values = [], []
    try:
        agg = (
            qs.filter(enrolled_at__gte=since)
            .annotate(d=TruncDay("enrolled_at"))
            .values("d")
            .annotate(n=Count("id"))
            .order_by("d")
        )
        chart_labels = [timezone.localtime(r["d"]).strftime("%d/%m") for r in agg]
        chart_values = [int(r["n"]) for r in agg]
    except Exception:
        chart_labels, chart_values = [], []

    # === Cards Statistiques ===
    cards = [
        StatCard(label=_("Inscriptions"), value=total, icon="🎓"),
        StatCard(label=_("Actives"), value=active_count, icon="🟢"),
        StatCard(label=_("Terminées"), value=completed_count, icon="✅"),
        StatCard(label=_("Certificats"), value=Certificate.objects.filter(enrollment__user=request.user).count(), icon="🏅"),
    ]

    return render(request, "dashboard/formations/home.html", {
        "page_title": _("Formations"),
        "breadcrumbs": breadcrumb((_('Dashboard'), "/dashboard/"), (_("Formations"), None)),
        "cards": [c.__dict__ for c in cards],
        "enrollments": enrollments,
        "total_count": total,
        "active_count": active_count,
        "completed_count": completed_count,
        "certificates": certs,
        "sessions": sessions,
        "calendar_enabled": calendar_enabled,
        "chart_labels": chart_labels,
        "chart_values": chart_values,
        "range_key": str(days),
    })


@login_required
def formations_courses_view(request):
    Enrollment, _Certificate, _CourseSession = _imports()

    q = (request.GET.get("q") or "").strip()
    status = (request.GET.get("status") or "").strip().upper()

    qs = Enrollment.objects.filter(user=request.user).select_related("course")
    has_status = _has_status_field(Enrollment)

    if has_status:
        cancelled = _status_cancelled_value(Enrollment)
        if cancelled:
            qs = qs.exclude(status=cancelled)

        allowed = {"PENDING", "ACTIVE", "COMPLETED"}
        if status in allowed:
            qs = qs.filter(status=status)

    if q:
        try:
            qs = qs.filter(course__translations__title__icontains=q)
        except Exception:
            qs = qs.filter(course__slug__icontains=q)

    enrollments = list(qs.order_by("-enrolled_at")[:250])

    return render(request, "dashboard/formations/courses.html", {
        "page_title": _("Mes cours"),
        "breadcrumbs": breadcrumb((_('Dashboard'), "/dashboard/"), (_("Formations"), "/dashboard/formations/"), (_("Cours"), None)),
        "enrollments": enrollments,
        "q": q,
        "status": status,
        "has_status": has_status,
    })


@login_required
def formations_calendar_view(request):
    Enrollment, _Certificate, CourseSession = _imports()

    if not CourseSession:
        return render(request, "dashboard/formations/calendar.html", {
            "page_title": _("Calendrier"),
            "breadcrumbs": breadcrumb((_('Dashboard'), "/dashboard/"), (_("Formations"), "/dashboard/formations/"), (_("Calendrier"), None)),
            "sessions": [],
            "calendar_unavailable": True,
        })

    now = timezone.now()
    range_days = _parse_range_days(request, default_days=90)

    dt_from = _safe_iso_datetime(request.GET.get("from"), now)
    dt_to = _safe_iso_datetime(request.GET.get("to"), now + timedelta(days=range_days))

    enroll_qs = Enrollment.objects.filter(user=request.user)
    if _has_status_field(Enrollment):
        cancelled = _status_cancelled_value(Enrollment)
        if cancelled:
            enroll_qs = enroll_qs.exclude(status=cancelled)

    course_ids = list(enroll_qs.values_list("course_id", flat=True).distinct()[:2000])

    sessions = list(
        CourseSession.objects.filter(course_id__in=course_ids, is_cancelled=False)
        .filter(starts_at__lt=dt_to, ends_at__gt=dt_from)
        .select_related("course")
        .order_by("starts_at")
    )

    return render(request, "dashboard/formations/calendar.html", {
        "page_title": _("Calendrier"),
        "breadcrumbs": breadcrumb((_('Dashboard'), "/dashboard/"), (_("Formations"), "/dashboard/formations/"), (_("Calendrier"), None)),
        "sessions": sessions,
        "calendar_unavailable": False,
        "dt_from": dt_from,
        "dt_to": dt_to,
        "range_key": str(range_days),
    })


@login_required
def formations_calendar_ics_view(request):
    Enrollment, _Certificate, CourseSession = _imports()
    if not CourseSession:
        raise Http404(_("Calendrier indisponible."))

    now = timezone.now()
    horizon = now + timedelta(days=180)

    enroll_qs = Enrollment.objects.filter(user=request.user)
    if _has_status_field(Enrollment):
        cancelled = _status_cancelled_value(Enrollment)
        if cancelled:
            enroll_qs = enroll_qs.exclude(status=cancelled)

    course_ids = list(enroll_qs.values_list("course_id", flat=True).distinct()[:2500])

    sessions = (
        CourseSession.objects.filter(course_id__in=course_ids, is_cancelled=False)
        .filter(starts_at__lt=horizon, ends_at__gt=now)
        .select_related("course")
        .order_by("starts_at")
    )

    lines: list[str] = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//SOGENTIS//Dashboard Formations Calendar//FR",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
    ]

    for s in sessions:
        uid = f"formation-session-{s.id}@sogentis"
        title = getattr(s, "title", "") or str(s.course)
        location = getattr(s, "location", "") or ""
        meeting_url = getattr(s, "meeting_url", "") or ""

        desc = ""
        if meeting_url:
            desc = f"{_('Lien')}: {meeting_url}"

        lines += [
            "BEGIN:VEVENT",
            f"UID:{_escape_ical(uid)}",
            f"DTSTAMP:{_dt_to_ical(timezone.now())}",
            f"DTSTART:{_dt_to_ical(timezone.localtime(s.starts_at))}",
            f"DTEND:{_dt_to_ical(timezone.localtime(s.ends_at))}",
            f"SUMMARY:{_escape_ical(title)}",
            f"LOCATION:{_escape_ical(location)}",
        ]
        if desc:
            lines.append(f"DESCRIPTION:{_escape_ical(desc)}")
        lines.append("END:VEVENT")

    lines.append("END:VCALENDAR")

    ics = "\r\n".join(lines) + "\r\n"
    resp = HttpResponse(ics, content_type="text/calendar; charset=utf-8")
    resp["Content-Disposition"] = 'attachment; filename="formations-calendar.ics"'
    return resp


@login_required
def formations_certificates_view(request):
    _Enrollment, Certificate, _CourseSession = _imports()

    certs = (
        Certificate.objects.filter(enrollment__user=request.user)
        .select_related("course", "enrollment")
        .order_by("-issued_at")
    )

    return render(request, "dashboard/formations/certificates.html", {
        "page_title": _("Mes certificats"),
        "breadcrumbs": breadcrumb((_('Dashboard'), "/dashboard/"), (_("Formations"), "/dashboard/formations/"), (_("Certificats"), None)),
        "certificates": certs,
    })


@login_required
def formations_certificate_download_view(request, uuid):
    _Enrollment, Certificate, _CourseSession = _imports()

    cert = get_object_or_404(Certificate, uuid=uuid, enrollment__user=request.user)

    pdf_field = getattr(cert, "pdf_file", None)
    if not pdf_field:
        try:
            from economic.formations.services.certificate_pdf import generate_certificate_pdf_and_attach
            generate_certificate_pdf_and_attach(cert, force=False)
        except Exception:
            pass

    pdf_field = getattr(cert, "pdf_file", None)
    if not pdf_field:
        raise Http404(_("PDF indisponible."))

    pdf_field.open("rb")
    filename = cert.download_filename() if hasattr(cert, "download_filename") else "certificate.pdf"
    return FileResponse(pdf_field, as_attachment=True, filename=filename)






# # dashboard/views/formations/formations.py 
# from __future__ import annotations

# from datetime import datetime, timedelta
# from typing import Optional

# from django.contrib.auth.decorators import login_required
# from django.db.models import Count
# from django.db.models.functions import TruncDay
# from django.http import FileResponse, Http404, HttpResponse
# from django.shortcuts import get_object_or_404, render
# from django.utils import timezone
# from django.utils.translation import gettext_lazy as _


# def _imports():
#     """
#     Imports safe (ne casse pas le dashboard si formations n'est pas encore migré).
#     """
#     try:
#         from economic.formations.models import Enrollment, Certificate
#     except Exception as exc:
#         raise Http404(_("Le module Formations n'est pas disponible.")) from exc

#     try:
#         from economic.formations.models import CourseSession
#     except Exception:
#         CourseSession = None  # type: ignore

#     return Enrollment, Certificate, CourseSession


# def _has_status_field(Enrollment) -> bool:
#     try:
#         Enrollment._meta.get_field("status")
#         return True
#     except Exception:
#         return False


# def _status_completed_value(Enrollment) -> Optional[str]:
#     st = getattr(Enrollment, "Status", None)
#     return getattr(st, "COMPLETED", None) if st else None


# def _status_cancelled_value(Enrollment) -> Optional[str]:
#     st = getattr(Enrollment, "Status", None)
#     return getattr(st, "CANCELLED", None) if st else None


# def _enrollment_is_completed(enrollment) -> bool:
#     if getattr(enrollment, "completed", False):
#         return True
#     completed_val = _status_completed_value(enrollment.__class__)
#     return bool(completed_val and getattr(enrollment, "status", None) == completed_val)


# def _dt_to_ical(dt: datetime) -> str:
#     dt_utc = timezone.make_naive(dt.astimezone(timezone.utc), timezone.utc)
#     return dt_utc.strftime("%Y%m%dT%H%M%SZ")


# def _escape_ical(text: str) -> str:
#     return (
#         (text or "")
#         .replace("\\", "\\\\")
#         .replace(";", r"\;")
#         .replace(",", r"\,")
#         .replace("\n", r"\n")
#     )


# def _parse_range_days(request, default_days: int = 30) -> int:
#     raw = (request.GET.get("range") or str(default_days)).strip()
#     if raw in {"7", "30", "90", "180"}:
#         return int(raw)
#     return default_days


# def _safe_iso_datetime(value: Optional[str], fallback: datetime) -> datetime:
#     if not value:
#         return fallback
#     try:
#         dt = datetime.fromisoformat(value)
#         if timezone.is_naive(dt):
#             dt = timezone.make_aware(dt)
#         return dt
#     except Exception:
#         return fallback


# @login_required
# def formations_home_view(request):
#     Enrollment, Certificate, CourseSession = _imports()

#     days = _parse_range_days(request, default_days=30)
#     since = timezone.now() - timedelta(days=days)

#     qs = Enrollment.objects.filter(user=request.user).select_related("course")

#     has_status = _has_status_field(Enrollment)
#     cancelled = _status_cancelled_value(Enrollment) if has_status else None
#     completed_val = _status_completed_value(Enrollment) if has_status else None

#     if cancelled:
#         qs = qs.exclude(status=cancelled)

#     qs = qs.order_by("-enrolled_at")

#     # ✅ Stats fiables
#     total = qs.count()

#     if completed_val:
#         completed_count = qs.filter(status=completed_val).count()
#     else:
#         # legacy: completed boolean
#         if hasattr(Enrollment, "completed"):
#             completed_count = qs.filter(completed=True).count()
#         else:
#             completed_count = 0

#     active_count = max(total - completed_count, 0)

#     # ✅ Dernières inscriptions
#     enrollments = list(qs[:10])

#     # ✅ Certificats récents
#     certs = (
#         Certificate.objects.filter(enrollment__user=request.user)
#         .select_related("course", "enrollment")
#         .order_by("-issued_at")[:6]
#     )

#     # ✅ Sessions à venir (si modèle dispo)
#     sessions = []
#     calendar_enabled = bool(CourseSession)
#     if CourseSession:
#         course_ids = list(qs.values_list("course_id", flat=True).distinct()[:1500])
#         if course_ids:
#             now = timezone.now()
#             sessions = list(
#                 CourseSession.objects.filter(course_id__in=course_ids, is_cancelled=False, ends_at__gte=now)
#                 .select_related("course")
#                 .order_by("starts_at")[:10]
#             )

#     # ✅ Chart (inscriptions/jour)
#     chart_labels, chart_values = [], []
#     try:
#         agg = (
#             qs.filter(enrolled_at__gte=since)
#             .annotate(d=TruncDay("enrolled_at"))
#             .values("d")
#             .annotate(n=Count("id"))
#             .order_by("d")
#         )
#         chart_labels = [timezone.localtime(r["d"]).strftime("%d/%m") for r in agg]
#         chart_values = [int(r["n"]) for r in agg]
#     except Exception:
#         chart_labels, chart_values = [], []

#     return render(request, "dashboard/formations/home.html", {
#         "range_key": str(days),

#         "enrollments": enrollments,
#         "total_count": total,
#         "active_count": active_count,
#         "completed_count": completed_count,

#         "certificates": certs,
#         "sessions": sessions,
#         "calendar_enabled": calendar_enabled,

#         "chart_labels": chart_labels,
#         "chart_values": chart_values,
#     })


# @login_required
# def formations_courses_view(request):
#     Enrollment, _Certificate, _CourseSession = _imports()

#     q = (request.GET.get("q") or "").strip()
#     status = (request.GET.get("status") or "").strip().upper()

#     qs = Enrollment.objects.filter(user=request.user).select_related("course")
#     has_status = _has_status_field(Enrollment)
#     cancelled = _status_cancelled_value(Enrollment) if has_status else None

#     if cancelled:
#         qs = qs.exclude(status=cancelled)

#     if has_status and status in {"PENDING", "ACTIVE", "COMPLETED"}:
#         qs = qs.filter(status=status)

#     if q:
#         try:
#             qs = qs.filter(course__translations__title__icontains=q)
#         except Exception:
#             qs = qs.filter(course__slug__icontains=q)

#     enrollments = list(qs.order_by("-enrolled_at")[:250])

#     return render(request, "dashboard/formations/courses.html", {
#         "enrollments": enrollments,
#         "q": q,
#         "status": status,
#         "has_status": has_status,
#     })


# @login_required
# def formations_calendar_view(request):
#     Enrollment, _Certificate, CourseSession = _imports()

#     if not CourseSession:
#         return render(request, "dashboard/formations/calendar.html", {
#             "sessions": [],
#             "calendar_unavailable": True,
#         })

#     now = timezone.now()

#     # ✅ fenêtre par défaut : range (90)
#     range_days = _parse_range_days(request, default_days=90)

#     dt_from = _safe_iso_datetime(request.GET.get("from"), now)
#     dt_to = _safe_iso_datetime(request.GET.get("to"), now + timedelta(days=range_days))

#     enroll_qs = Enrollment.objects.filter(user=request.user)
#     if _has_status_field(Enrollment):
#         cancelled = _status_cancelled_value(Enrollment)
#         if cancelled:
#             enroll_qs = enroll_qs.exclude(status=cancelled)

#     course_ids = list(enroll_qs.values_list("course_id", flat=True).distinct()[:2000])

#     sessions = list(
#         CourseSession.objects.filter(course_id__in=course_ids, is_cancelled=False)
#         .filter(starts_at__lt=dt_to, ends_at__gt=dt_from)
#         .select_related("course")
#         .order_by("starts_at")
#     )

#     return render(request, "dashboard/formations/calendar.html", {
#         "sessions": sessions,
#         "calendar_unavailable": False,
#         "dt_from": dt_from,
#         "dt_to": dt_to,
#         "range_key": str(range_days),
#     })


# @login_required
# def formations_calendar_ics_view(request):
#     Enrollment, _Certificate, CourseSession = _imports()

#     if not CourseSession:
#         raise Http404(_("Calendrier indisponible."))

#     now = timezone.now()
#     horizon = now + timedelta(days=180)

#     enroll_qs = Enrollment.objects.filter(user=request.user)
#     if _has_status_field(Enrollment):
#         cancelled = _status_cancelled_value(Enrollment)
#         if cancelled:
#             enroll_qs = enroll_qs.exclude(status=cancelled)

#     course_ids = list(enroll_qs.values_list("course_id", flat=True).distinct()[:2500])

#     sessions = (
#         CourseSession.objects.filter(course_id__in=course_ids, is_cancelled=False)
#         .filter(starts_at__lt=horizon, ends_at__gt=now)
#         .select_related("course")
#         .order_by("starts_at")
#     )

#     lines: list[str] = [
#         "BEGIN:VCALENDAR",
#         "VERSION:2.0",
#         "PRODID:-//SOGENTIS//Dashboard Formations Calendar//FR",
#         "CALSCALE:GREGORIAN",
#         "METHOD:PUBLISH",
#     ]

#     for s in sessions:
#         uid = f"formation-session-{s.id}@sogentis"
#         title = getattr(s, "title", "") or str(s.course)
#         location = getattr(s, "location", "") or ""
#         meeting_url = getattr(s, "meeting_url", "") or ""

#         desc = ""
#         if meeting_url:
#             desc = f"{_('Lien')}: {meeting_url}"

#         lines += [
#             "BEGIN:VEVENT",
#             f"UID:{_escape_ical(uid)}",
#             f"DTSTAMP:{_dt_to_ical(timezone.now())}",
#             f"DTSTART:{_dt_to_ical(timezone.localtime(s.starts_at))}",
#             f"DTEND:{_dt_to_ical(timezone.localtime(s.ends_at))}",
#             f"SUMMARY:{_escape_ical(title)}",
#             f"LOCATION:{_escape_ical(location)}",
#         ]
#         if desc:
#             lines.append(f"DESCRIPTION:{_escape_ical(desc)}")
#         lines.append("END:VEVENT")

#     lines.append("END:VCALENDAR")

#     ics = "\r\n".join(lines) + "\r\n"
#     resp = HttpResponse(ics, content_type="text/calendar; charset=utf-8")
#     resp["Content-Disposition"] = 'attachment; filename="formations-calendar.ics"'
#     return resp


# @login_required
# def formations_certificates_view(request):
#     _Enrollment, Certificate, _CourseSession = _imports()

#     certs = (
#         Certificate.objects.filter(enrollment__user=request.user)
#         .select_related("course", "enrollment")
#         .order_by("-issued_at")
#     )
#     return render(request, "dashboard/formations/certificates.html", {"certificates": certs})


# @login_required
# def formations_certificate_download_view(request, uuid):
#     _Enrollment, Certificate, _CourseSession = _imports()

#     cert = get_object_or_404(Certificate, uuid=uuid, enrollment__user=request.user)

#     # Générer PDF si absent (si ton service existe)
#     pdf_field = getattr(cert, "pdf_file", None)
#     if not pdf_field:
#         try:
#             from economic.formations.services.certificate_pdf import generate_certificate_pdf_and_attach
#             generate_certificate_pdf_and_attach(cert, force=False)
#         except Exception:
#             pass

#     pdf_field = getattr(cert, "pdf_file", None)
#     if not pdf_field:
#         raise Http404(_("PDF indisponible."))

#     pdf_field.open("rb")
#     filename = cert.download_filename() if hasattr(cert, "download_filename") else "certificate.pdf"
#     return FileResponse(pdf_field, as_attachment=True, filename=filename)





# # dashboard/views/formations/formations.py
# from __future__ import annotations

# from datetime import datetime, timedelta
# from typing import Iterable, Optional

# from django.contrib.auth.decorators import login_required
# from django.http import FileResponse, Http404, HttpResponse
# from django.shortcuts import get_object_or_404, render
# from django.utils import timezone
# from django.utils.translation import gettext_lazy as _


# def _imports():
#     """
#     Imports safe (ne casse pas le dashboard si formations n'est pas encore migré).
#     """
#     try:
#         from economic.formations.models import Enrollment, Certificate
#     except Exception as exc:
#         raise Http404(_("Le module Formations n'est pas disponible.")) from exc

#     try:
#         from economic.formations.models import CourseSession
#     except Exception:
#         CourseSession = None  # type: ignore

#     return Enrollment, Certificate, CourseSession


# def _has_status_field(Enrollment) -> bool:
#     try:
#         Enrollment._meta.get_field("status")
#         return True
#     except Exception:
#         return False


# def _status_completed_value(Enrollment) -> Optional[str]:
#     # Enrollment.Status.COMPLETED si présent
#     st = getattr(Enrollment, "Status", None)
#     return getattr(st, "COMPLETED", None) if st else None


# def _status_cancelled_value(Enrollment) -> Optional[str]:
#     st = getattr(Enrollment, "Status", None)
#     return getattr(st, "CANCELLED", None) if st else None


# def _enrollment_is_completed(enrollment) -> bool:
#     if getattr(enrollment, "completed", False):
#         return True
#     st = getattr(enrollment, "status", None)
#     completed_val = _status_completed_value(enrollment.__class__)
#     return bool(completed_val and st == completed_val)


# def _enrollment_is_cancelled(enrollment) -> bool:
#     st = getattr(enrollment, "status", None)
#     cancelled_val = _status_cancelled_value(enrollment.__class__)
#     return bool(cancelled_val and st == cancelled_val)


# def _dt_to_ical(dt: datetime) -> str:
#     # iCal requires UTC "Z"
#     dt_utc = timezone.make_naive(dt.astimezone(timezone.utc), timezone.utc)
#     return dt_utc.strftime("%Y%m%dT%H%M%SZ")


# def _escape_ical(text: str) -> str:
#     return (
#         (text or "")
#         .replace("\\", "\\\\")
#         .replace(";", r"\;")
#         .replace(",", r"\,")
#         .replace("\n", r"\n")
#     )


# @login_required
# def formations_home_view(request):
#     Enrollment, Certificate, CourseSession = _imports()

#     qs = Enrollment.objects.filter(user=request.user).select_related("course")
#     if _has_status_field(Enrollment):
#         cancelled = _status_cancelled_value(Enrollment)
#         if cancelled:
#             qs = qs.exclude(status=cancelled)

#     qs = qs.order_by("-enrolled_at")

#     enrollments = list(qs[:10])
#     course_ids = [e.course_id for e in enrollments]

#     # Stats
#     total = qs.count()
#     completed_count = sum(1 for e in enrollments if _enrollment_is_completed(e))
#     active_count = max(total - completed_count, 0)

#     # Certificats récents
#     certs = (
#         Certificate.objects.filter(enrollment__user=request.user)
#         .select_related("course", "enrollment")
#         .order_by("-issued_at")[:6]
#     )

#     # Sessions à venir (si modèle dispo)
#     sessions = []
#     if CourseSession and course_ids:
#         now = timezone.now()
#         sessions = list(
#             CourseSession.objects.filter(course_id__in=course_ids, is_cancelled=False, ends_at__gte=now)
#             .select_related("course")
#             .order_by("starts_at")[:10]
#         )

#     return render(request, "dashboard/formations/home.html", {
#         "enrollments": enrollments,
#         "total_count": total,
#         "active_count": active_count,
#         "completed_count": completed_count,
#         "certificates": certs,
#         "sessions": sessions,
#     })


# @login_required
# def formations_courses_view(request):
#     Enrollment, _Certificate, _CourseSession = _imports()

#     q = (request.GET.get("q") or "").strip()
#     status = (request.GET.get("status") or "").strip().upper()

#     qs = Enrollment.objects.filter(user=request.user).select_related("course")
#     if _has_status_field(Enrollment):
#         cancelled = _status_cancelled_value(Enrollment)
#         if cancelled:
#             qs = qs.exclude(status=cancelled)

#         if status in {"PENDING", "ACTIVE", "COMPLETED"}:
#             qs = qs.filter(status=status)

#     # Recherche titre cours (Parler-friendly via __str__/safe_translation_getter => on fait simple ici)
#     if q:
#         # si Course est Translatable, title est dans translations -> on tente, sinon fallback
#         try:
#             qs = qs.filter(course__translations__title__icontains=q)
#         except Exception:
#             qs = qs.filter(course__slug__icontains=q)

#     enrollments = list(qs.order_by("-enrolled_at")[:200])

#     return render(request, "dashboard/formations/courses.html", {
#         "enrollments": enrollments,
#         "q": q,
#         "status": status,
#         "has_status": _has_status_field(Enrollment),
#     })


# @login_required
# def formations_calendar_view(request):
#     Enrollment, _Certificate, CourseSession = _imports()
#     if not CourseSession:
#         return render(request, "dashboard/formations/calendar.html", {
#             "sessions": [],
#             "calendar_unavailable": True,
#         })

#     now = timezone.now()

#     # fenêtre de base : 90 jours
#     date_from = request.GET.get("from")
#     date_to = request.GET.get("to")

#     try:
#         dt_from = timezone.make_aware(datetime.fromisoformat(date_from)) if date_from else now
#     except Exception:
#         dt_from = now

#     try:
#         dt_to = timezone.make_aware(datetime.fromisoformat(date_to)) if date_to else now + timedelta(days=90)
#     except Exception:
#         dt_to = now + timedelta(days=90)

#     enroll_qs = Enrollment.objects.filter(user=request.user)
#     if _has_status_field(Enrollment):
#         cancelled = _status_cancelled_value(Enrollment)
#         if cancelled:
#             enroll_qs = enroll_qs.exclude(status=cancelled)

#     course_ids = list(enroll_qs.values_list("course_id", flat=True))

#     sessions = list(
#         CourseSession.objects.filter(course_id__in=course_ids, is_cancelled=False)
#         .filter(starts_at__lt=dt_to, ends_at__gt=dt_from)
#         .select_related("course")
#         .order_by("starts_at")
#     )

#     return render(request, "dashboard/formations/calendar.html", {
#         "sessions": sessions,
#         "calendar_unavailable": False,
#         "dt_from": dt_from,
#         "dt_to": dt_to,
#     })


# @login_required
# def formations_calendar_ics_view(request):
#     Enrollment, _Certificate, CourseSession = _imports()
#     if not CourseSession:
#         raise Http404(_("Calendrier indisponible."))

#     now = timezone.now()
#     horizon = now + timedelta(days=180)

#     enroll_qs = Enrollment.objects.filter(user=request.user)
#     if _has_status_field(Enrollment):
#         cancelled = _status_cancelled_value(Enrollment)
#         if cancelled:
#             enroll_qs = enroll_qs.exclude(status=cancelled)

#     course_ids = list(enroll_qs.values_list("course_id", flat=True))

#     sessions = (
#         CourseSession.objects.filter(course_id__in=course_ids, is_cancelled=False)
#         .filter(starts_at__lt=horizon, ends_at__gt=now)
#         .select_related("course")
#         .order_by("starts_at")
#     )

#     lines: list[str] = [
#         "BEGIN:VCALENDAR",
#         "VERSION:2.0",
#         "PRODID:-//SOGENTIS//Formations Calendar//FR",
#         "CALSCALE:GREGORIAN",
#         "METHOD:PUBLISH",
#     ]

#     for s in sessions:
#         uid = f"formation-session-{s.id}@sogentis"
#         title = getattr(s, "title", "") or str(s.course)
#         location = getattr(s, "location", "") or ""
#         desc_parts = []
#         meeting_url = getattr(s, "meeting_url", "") or ""
#         if meeting_url:
#             desc_parts.append(f"{_('Lien')}: {meeting_url}")
#         desc = "\n".join(desc_parts)

#         lines += [
#             "BEGIN:VEVENT",
#             f"UID:{_escape_ical(uid)}",
#             f"DTSTAMP:{_dt_to_ical(timezone.now())}",
#             f"DTSTART:{_dt_to_ical(timezone.localtime(s.starts_at))}",
#             f"DTEND:{_dt_to_ical(timezone.localtime(s.ends_at))}",
#             f"SUMMARY:{_escape_ical(title)}",
#             f"LOCATION:{_escape_ical(location)}",
#         ]
#         if desc:
#             lines.append(f"DESCRIPTION:{_escape_ical(desc)}")
#         lines.append("END:VEVENT")

#     lines.append("END:VCALENDAR")

#     ics = "\r\n".join(lines) + "\r\n"
#     resp = HttpResponse(ics, content_type="text/calendar; charset=utf-8")
#     resp["Content-Disposition"] = 'attachment; filename="formations-calendar.ics"'
#     return resp


# @login_required
# def formations_certificates_view(request):
#     _Enrollment, Certificate, _CourseSession = _imports()
#     certs = (
#         Certificate.objects.filter(enrollment__user=request.user)
#         .select_related("course", "enrollment")
#         .order_by("-issued_at")
#     )
#     return render(request, "dashboard/formations/certificates.html", {"certificates": certs})


# @login_required
# def formations_certificate_download_view(request, uuid):
#     _Enrollment, Certificate, _CourseSession = _imports()

#     cert = get_object_or_404(Certificate, uuid=uuid, enrollment__user=request.user)

#     # Générer PDF si absent (service déjà fourni)
#     if not getattr(cert, "pdf_file", None):
#         try:
#             from economic.formations.services.certificate_pdf import generate_certificate_pdf_and_attach
#             generate_certificate_pdf_and_attach(cert, force=False)
#         except Exception as exc:
#             raise Http404(_("PDF indisponible.")) from exc

#     if not cert.pdf_file:
#         raise Http404(_("PDF indisponible."))

#     # Secure file response
#     cert.pdf_file.open("rb")
#     filename = cert.download_filename() if hasattr(cert, "download_filename") else "certificate.pdf"
#     return FileResponse(cert.pdf_file, as_attachment=True, filename=filename)
