# stakeholders/beneficiaries/views.py

from django.shortcuts import render

def beneficiaries_list(request):
    # logique ici
    return render(request, "stakeholders/beneficiaries_list.html")



def regions_covered(request):
    # logique ici
    return render(request, "stakeholders/regions_covered.html")
