#social/views/volunteers.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from ..forms import EngagementForm


@login_required
def engagement_view(request):
    """
    Permet à un utilisateur connecté de s’engager comme bénévole.
    """
    if request.method == 'POST':
        form = EngagementForm(request.POST)
        if form.is_valid():
            engagement = form.save(commit=False)
            engagement.user = request.user
            engagement.save()
            messages.success(request, _("Merci pour votre engagement !"))
            return redirect('dashboard:index')
    else:
        form = EngagementForm()

    return render(request, 'social/volunteers/become_volunteer.html', {'form': form})
