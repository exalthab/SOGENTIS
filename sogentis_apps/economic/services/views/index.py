# economic/services/views/services_list.py
from django.shortcuts import render
from ..models.service import Service


def services_index_view(request):
    return render(request, "economic/services/index.html", {
        "services": Service.objects.all()
    })
