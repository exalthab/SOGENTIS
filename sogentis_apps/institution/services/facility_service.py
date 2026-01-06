from django.shortcuts import get_object_or_404

from institution.models.facility import Facility


def get_active_facilities():
    return Facility.objects.filter(is_active=True).order_by("-created_at")


def get_facility_by_slug(slug: str) -> Facility:
    return get_object_or_404(Facility, slug=slug, is_active=True)
