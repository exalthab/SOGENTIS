# economic/formations/urls.py
from django.urls import path

from .views.index_catalog import formations_index_view
from .views.course_list import course_list_view
from .views.course_detail import course_detail_view
from .views.enrollment import enroll_view
from .views.learning import learning_view
from .views.certificates import (
    certificates_view,
    certificate_detail_view,
    certificate_download_view,
)

# ✅ NOUVEAUX (pour activer les liens du menu)
from .views.my_dashboard import my_dashboard_view
from .views.my_calendar import my_calendar_view
from .views.my_courses import my_courses_view

app_name = "formations"

urlpatterns = [
    path("", formations_index_view, name="index"),

    path("courses/", course_list_view, name="course_list"),
    path("courses/<slug:slug>/", course_detail_view, name="course_detail"),
    path("courses/<slug:slug>/enroll/", enroll_view, name="enroll"),

    path("learning/<slug:slug>/", learning_view, name="learning"),

    # ✅ Espace apprenant (ACTIF)
    path("my/", my_dashboard_view, name="my_dashboard"),
    path("my/courses/", my_courses_view, name="my_courses"),
    path("my/calendar/", my_calendar_view, name="my_calendar"),

    # ✅ Certificats (déjà ok)
    path("my/certificates/", certificates_view, name="my_certificates"),
    path("my/certificates/<uuid:uuid>/", certificate_detail_view, name="certificate_detail"),
    path("my/certificates/<uuid:uuid>/download/", certificate_download_view, name="certificate_download"),
]



# # economic/formations/urls.py
# from django.urls import path

# from .views.catalog_2 import formations_index_view
# from .views.course_list import course_list_view
# from .views.course_detail import course_detail_view
# from .views.enrollment import enroll_view
# from .views.learning import learning_view
# from .views.certificates import certificates_view, certificate_detail_view, certificate_download_view

# # ✅ NOUVEAU
# from .views.my_dashboard import my_dashboard_view
# from .views.my_courses import my_courses_view
# from .views.my_calendar import my_calendar_view

# app_name = "formations"

# urlpatterns = [
#     path("", formations_index_view, name="index"),

#     path("courses/", course_list_view, name="course_list"),
#     path("courses/<slug:slug>/", course_detail_view, name="course_detail"),
#     path("courses/<slug:slug>/enroll/", enroll_view, name="enroll"),

#     path("learning/<slug:slug>/", learning_view, name="learning"),

#     # ✅ Espace apprenant (créé)
#     path("my/", my_dashboard_view, name="my_dashboard"),
#     path("my/courses/", my_courses_view, name="my_courses"),
#     path("my/calendar/", my_calendar_view, name="my_calendar"),

#     # Certificats
#     path("my/certificates/", certificates_view, name="my_certificates"),
#     path("my/certificates/<uuid:uuid>/", certificate_detail_view, name="certificate_detail"),
#     path("my/certificates/<uuid:uuid>/download/", certificate_download_view, name="certificate_download"),
# ]





# # economic/formations/urls.py

# from django.urls import path

# from .views import (
#     index,
#     course_detail,
#     learning,
#     certificates,
#     course_list,
#     enrollment,
# )

# app_name = "formations"

# urlpatterns = [
#     # Accueil du pôle formations
#     path(
#         "",
#         index.formations_index_view,
#         name="index",
#     ),

#     # Catalogue des formations
#     path(
#         "catalogue/",
#         course_list.course_list_view,
#         name="course_list",
#     ),

#     # Détail d'une formation
#     path(
#         "courses/<slug:slug>/",
#         course_detail.course_detail_view,
#         name="course_detail",
#     ),

#     # Espace d'apprentissage (contenu de la formation)
#     path(
#         "courses/<slug:slug>/learn/",
#         learning.learning_view,
#         name="learning",
#     ),

#     # Inscription à une formation
#     path(
#         "courses/<slug:slug>/enroll/",
#         enrollment.enroll_view,
#         name="enroll",
#     ),

#     # Certificats
#     path(
#         "certificates/",
#         certificates.certificates_view,
#         name="certificates",
#     ),
# ]







# # economic/formations/urls.py
# from django.urls import path
# from .views import course_detail, index, learning, certificates

# app_name = "formations"

# urlpatterns = [
#     path("", index.formations_index_view, name="index"),
#     path("<slug:slug>/", course_detail.course_detail_view, name="course_detail"),
#     path("<slug:slug>/learn/", learning.learning_view, name="learning"),
#     path("certificates/", certificates.certificates_view, name="certificates"),
# ]
