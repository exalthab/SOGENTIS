# economic/urls.py
from __future__ import annotations

from django.urls import include, path

from economic.views import economic_home_view

app_name = "economic"

urlpatterns = [
    path("", economic_home_view, name="index"),
    path("api/", include(("economic.api.urls", "api"), namespace="api")),
    path("b2b/", include(("economic.b2b.urls", "b2b"), namespace="b2b")),
    path("ecommerce/", include(("economic.ecommerce.urls", "ecommerce"), namespace="ecommerce")),
    path("formations/", include(("economic.formations.urls", "formations"), namespace="formations")),
    path("resources/", include(("economic.resources.urls", "resources"), namespace="resources")),
    path("prestations/", include(("economic.prestations.urls", "prestations"), namespace="prestations")),
    path("support/", include(("economic.support.urls", "support"), namespace="support")),
]







# # economic/urls.py
# from django.urls import path, include
# from django.utils.translation import gettext_lazy as _

# from .views import economic_home_view

# app_name = "economic"

# urlpatterns = [
#     # Home économique
#     path("", economic_home_view, name="index"),

#     # About (si tu veux le garder ici)
#     path("about/", include(("about.urls", "about"), namespace="about")),

#     # Sous-apps
#     path(_("shop/"), include(("economic.ecommerce.urls", "ecommerce"), namespace="ecommerce")),
#     path(_("formations/"), include(("economic.formations.urls", "formations"), namespace="formations")),
#     path(_("services/"), include(("economic.services.urls", "services"), namespace="services")),
#     path(_("b2b/"), include(("economic.b2b.urls", "b2b"), namespace="b2b")),
#     path(_("resources/"), include(("economic.resources.urls", "resources"), namespace="resources")),
#     path(_("support/"), include(("economic.support.urls", "support"), namespace="support")),
# ]




# # economic/urls.py
# from django.urls import path, include
# from django.utils.translation import gettext_lazy as _
# from .views import economic_home_view

# app_name = "economic"

# urlpatterns = [
#     # Page d'accueil du pôle économique
#     path("", economic_home_view, name="index"),
#     path("", include(("core.urls", "core"), namespace="core")),
#     # path("economic/", include(("economic.urls", "economic"), namespace="economic")),
#     path("about/", include(("about.urls", "about"), namespace="about")),

#     # Sous-apps du pôle économique
#     path(_("shop/"), include(("economic.ecommerce.urls", "ecommerce"), namespace="ecommerce")),
#     path(_("formations/"), include(("economic.formations.urls", "formations"), namespace="formations")),
#     path(_("services/"), include(("economic.services.urls", "services"), namespace="services")),
#     path(_("b2b/"), include(("economic.b2b.urls", "b2b"), namespace="b2b")),
#     path(_("resources/"), include(("economic.resources.urls", "resources"), namespace="resources")),
#     path(_("support/"), include(("economic.support.urls", "support"), namespace="support")),
# ]






# # sogentis_apps/economic/urls.py

# from django.urls import path, include
# from django.utils.translation import gettext_lazy as _
# from .views import economic_home_view

# app_name = "economic"

# urlpatterns = [
#     # Page d'accueil du pôle économique
#     path("", economic_home_view, name="home"),

#     # Sous-apps du pôle économique
#     path(_("shop/"), include("sogentis_apps.economic.ecommerce.urls")),
#     path(_("formations/"), include("sogentis_apps.economic.formations.urls")),
#     path(_("services/"), include("sogentis_apps.economic.services.urls")),
#     path(_("b2b/"), include("sogentis_apps.economic.b2b.urls")),
#     path(_("resources/"), include("sogentis_apps.economic.resources.urls")),
#     path(_("support/"), include("sogentis_apps.economic.support.urls")),
# ]









# # /economic/urls.py
# from django.urls import path, include
# from django.utils.translation import gettext_lazy as _
# from .views import economic_home_view

# app_name = "economic"

# urlpatterns = [
#     path("", economic_home_view, name="home"),

#     # path("shop/", include("sogentis_apps.economic.ecommerce.urls")),
#     # path(_("formations/"), include("sogentis_apps.economic.formations.urls")),
#     # path(_("services/"), include("sogentis_apps.economic.services.urls")),
#     # path(_("b2b/"), include("sogentis_apps.economic.b2b.urls")),
#     # path(_("resources/"), include("sogentis_apps.economic.resources.urls")),
#     # path(_("support/"), include("sogentis_apps.economic.support.urls")),
#  ]



# from . import views

    # path("cart/", views.cart_detail, name="cart_detail"),
    # path("shop/", views.shop_view, name="shop"),
    # path("", views.econ_index, name="econ_index"),