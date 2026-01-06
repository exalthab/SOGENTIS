from django.shortcuts import render

from institution.services.program_service import get_active_programs, get_program_by_slug


def program_list_view(request):
    programs = get_active_programs()
    return render(request, "institution/programs/program_list.html", {"programs": programs})


def program_detail_view(request, slug: str):
    program = get_program_by_slug(slug)
    return render(request, "institution/programs/program_detail.html", {"program": program})
