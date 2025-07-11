from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from .forms import VolunteerForm

def become_volunteer(request):
    if request.method == "POST":
        form = VolunteerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Merci pour votre engagement !")
            return redirect(reverse("volunteers:thanks"))
    else:
        form = VolunteerForm()

    return render(request, "volunteers/become_volunteer.html", {"form": form})

def thanks(request):
    return render(request, "volunteers/thanks.html")
