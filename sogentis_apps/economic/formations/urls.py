# economic/formations/urls.py

from django.urls import path

from .views import (
    index,
    course_detail,
    learning,
    certificates,
    course_list,
    enrollment,
)

app_name = "formations"

urlpatterns = [
    # Accueil du pôle formations
    path(
        "",
        index.formations_index_view,
        name="index",
    ),

    # Catalogue des formations
    path(
        "catalogue/",
        course_list.course_list_view,
        name="course_list",
    ),

    # Détail d'une formation
    path(
        "courses/<slug:slug>/",
        course_detail.course_detail_view,
        name="course_detail",
    ),

    # Espace d'apprentissage (contenu de la formation)
    path(
        "courses/<slug:slug>/learn/",
        learning.learning_view,
        name="learning",
    ),

    # Inscription à une formation
    path(
        "courses/<slug:slug>/enroll/",
        enrollment.enroll_view,
        name="enroll",
    ),

    # Certificats
    path(
        "certificates/",
        certificates.certificates_view,
        name="certificates",
    ),
]







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
