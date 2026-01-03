# economic/urls.py
from django.urls import path, include
from django.utils.translation import gettext_lazy as _
from .views import economic_home_view

app_name = "economic"

urlpatterns = [
    # Page d'accueil du pôle économique
    path("", economic_home_view, name="index"),

    # Sous-apps du pôle économique
    path(_("shop/"), include(("economic.ecommerce.urls", "ecommerce"), namespace="index")),
    path(_("formations/"), include(("economic.formations.urls", "formations"), namespace="formations")),
    path(_("services/"), include(("economic.services.urls", "services"), namespace="services")),
    path(_("b2b/"), include(("economic.b2b.urls", "b2b"), namespace="b2b")),
    path(_("resources/"), include(("economic.resources.urls", "resources"), namespace="resources")),
    path(_("support/"), include(("economic.support.urls", "support"), namespace="support")),
]






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