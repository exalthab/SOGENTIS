from django.urls import include, path

urlpatterns = [
    path("", include("accounts_users.web.urls.registration_urls")),
]
