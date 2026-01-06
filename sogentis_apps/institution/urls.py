from django.urls import path

from institution.views.index import institution_home_view
from institution.views.schools import schools_home_view
from institution.views.health import health_home_view
from institution.views.youth import youth_home_view

from institution.views.facilities import facility_list_view, facility_detail_view
from institution.views.programs import program_list_view, program_detail_view


app_name = "institution"

urlpatterns = [
    path("", institution_home_view, name="index"),
    path("ecoles/", schools_home_view, name="schools"),
    path("sante/", health_home_view, name="health"),
    path("jeunesse/", youth_home_view, name="youth"),
    # Facilities (école, centre loisirs, centre santé, etc.)
    path("structures/", facility_list_view, name="facility_list"),
    path("structures/<slug:slug>/", facility_detail_view, name="facility_detail"),

    # Programs (programmes / activités liés à une structure)
    path("programmes/", program_list_view, name="program_list"),
    path("programmes/<slug:slug>/", program_detail_view, name="program_detail"),

]
