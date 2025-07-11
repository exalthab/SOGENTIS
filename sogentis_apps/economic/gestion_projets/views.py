#economic/gestions_projets/views.py (services)
from django.shortcuts import render, get_object_or_404
from economic.gestion_projets.models import Service

def services_list(request):
    services = Service.objects.filter(is_active=True)
    return render(request, 'economic/services_list.html', {
        'services': services
    })

def service_detail_view(request, slug):
    service = get_object_or_404(Service, slug=slug, is_active=True)
    return render(request, 'economic/service_detail.html', {
        'service': service
    })

