#economic/formations/views.py
from django.shortcuts import render, get_object_or_404
from economic.formations.models import Formation

def formations_list(request):
    formations = Formation.objects.filter(is_active=True)
    return render(request, 'economic/formations_list.html', {
        'formations': formations
    })

def formation_details_view(request, slug):
    formation = get_object_or_404(Formation, slug=slug, is_active=True)
    return render(request, 'economic/formation_detail.html', {
        'formation': formation
    })
