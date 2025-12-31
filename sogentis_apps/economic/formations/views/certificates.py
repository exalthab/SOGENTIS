# economic/formations/views/certificates.py
from django.shortcuts import render


def certificates_view(request):
    return render(request, "formations/certificates.html")
