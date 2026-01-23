# dashboard/urls/formations.py
from django.urls import path

try:
    # si tu as dashboard/views/formations/formations.py
    from dashboard.views.formations.formations import (
        formations_home_view,
        formations_courses_view,
        formations_calendar_view,
        formations_calendar_ics_view,
        formations_certificates_view,
        formations_certificate_download_view,
    )
except Exception:
    # fallback si tu as encore dashboard/views/formations.py (fichier plat)
    from dashboard.views.formations import (  # type: ignore
        formations_home_view,
        formations_courses_view,
        formations_calendar_view,
        formations_calendar_ics_view,
        formations_certificates_view,
        formations_certificate_download_view,
    )

app_name = "dashboard_formations"

urlpatterns = [
    path("", formations_home_view, name="home"),
    path("courses/", formations_courses_view, name="courses"),
    path("calendar/", formations_calendar_view, name="calendar"),
    path("calendar.ics", formations_calendar_ics_view, name="calendar_ics"),
    path("certificates/", formations_certificates_view, name="certificates"),
    path("certificates/<uuid:uuid>/download/", formations_certificate_download_view, name="certificate_download"),
]






# # dashboard/urls/formations.py
# from django.urls import path
# from dashboard.views.formations.formations import (
#     formations_home_view,
#     formations_courses_view,
#     formations_calendar_view,
#     formations_calendar_ics_view,
#     formations_certificates_view,
#     formations_certificate_download_view,
# )
 
# app_name = "dashboard_formations" 

# urlpatterns = [
#     path("", formations_home_view, name="home"),
#     path("courses/", formations_courses_view, name="courses"),
#     path("calendar/", formations_calendar_view, name="calendar"),
#     path("calendar.ics", formations_calendar_ics_view, name="calendar_ics"),
#     path("certificates/", formations_certificates_view, name="certificates"),
#     path("certificates/<uuid:uuid>/download/", formations_certificate_download_view, name="certificate_download"),
# ]



# # dashboard/urls.py (ajout)
# from django.urls import path

# from dashboard.views.formations import (
#     formations_home_view,
#     formations_courses_view,
#     formations_calendar_view,
#     formations_calendar_ics_view,
#     formations_certificates_view,
#     formations_certificate_download_view,
# )

# app_name = "formations"

# urlpatterns = [
#     path("formations/", formations_home_view, name="formations_home"),
#     path("formations/courses/", formations_courses_view, name="formations_courses"),
#     path("formations/calendar/", formations_calendar_view, name="formations_calendar"),
#     path("formations/calendar.ics", formations_calendar_ics_view, name="formations_calendar_ics"),
#     path("formations/certificates/", formations_certificates_view, name="formations_certificates"),
#     path("formations/certificates/<uuid:uuid>/download/", formations_certificate_download_view, name="formations_certificate_download"),
# ]
