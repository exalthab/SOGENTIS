from django.shortcuts import render

from institution.services.facility_service import get_active_facilities, get_facility_by_slug


def facility_list_view(request):
    facilities = get_active_facilities()
    return render(request, "institution/facilities/facility_list.html", {"facilities": facilities})


def facility_detail_view(request, slug: str):
    facility = get_facility_by_slug(slug)
    return render(request, "institution/facilities/facility_detail.html", {"facility": facility})
