# economic/services/views/service_detail.py
from django.shortcuts import render, get_object_or_404
from ..models.service import Service

def service_detail_view(request, slug):
    service = get_object_or_404(
        Service,
        slug=slug,  # make sure Service has a 'slug' field
        is_active=True
    )
    return render(request, "economic/services/service_detail.html", {"service": service})
