from django.shortcuts import get_object_or_404

from institution.models.program import Program


def get_active_programs():
    return Program.objects.select_related("facility").filter(is_active=True).order_by("-created_at")


def get_program_by_slug(slug: str) -> Program:
    return get_object_or_404(Program.objects.select_related("facility"), slug=slug, is_active=True)
