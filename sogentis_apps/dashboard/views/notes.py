# # #dashboard/views/notes.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from dashboard.models.dashboard_note import DashboardNote
from dashboard.forms.note_form import DashboardNoteForm

@login_required
def create_note_view(request):
    if request.method == 'POST':
        form = DashboardNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.author = request.user  # <-- Corrigé : 'author'
            note.save()
            messages.success(request, _("Note créée avec succès."))
            return redirect('dashboard:notes_list')
    else:
        form = DashboardNoteForm()
    return render(request, 'dashboard/notes/note_form.html', {
        'form': form,
        'title': _("Créer une note")
    })

@login_required
def edit_note_view(request, pk):
    note = get_object_or_404(DashboardNote, pk=pk, author=request.user)
    if request.method == 'POST':
        form = DashboardNoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, _("Note mise à jour avec succès."))
            return redirect('dashboard:notes_list')
    else:
        form = DashboardNoteForm(instance=note)
    return render(request, 'dashboard/notes/note_form.html', {
        'form': form,
        'title': _("Modifier la note")
    })

@login_required
def note_list_view(request):
    notes = DashboardNote.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'dashboard/notes/notes_list.html', {
        'notes': notes,
        'title': _("Mes notes")
    })



# # #dashboard/views/notes.py
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render, redirect, get_object_or_404
# from dashboard.models.dashboard_note import DashboardNote
# from dashboard.forms.note_form import DashboardNoteForm

# @login_required
# def note_list_view(request):
#     notes = DashboardNote.objects.filter(user=request.user)
#     return render(request, "dashboard/notes_list.html", {"notes": notes})

# @login_required
# def create_note_view(request):
#     if request.method == "POST":
#         form = DashboardNoteForm(request.POST)
#         if form.is_valid():
#             note = form.save(commit=False)
#             note.user = request.user
#             note.save()
#             return redirect("dashboard:notes_list")
#     else:
#         form = DashboardNoteForm()
#     return render(request, "dashboard/note_form.html", {"form": form})

# @login_required
# def edit_note_view(request, pk):
#     note = get_object_or_404(DashboardNote, pk=pk, user=request.user)
#     if request.method == "POST":
#         form = DashboardNoteForm(request.POST, instance=note)
#         if form.is_valid():
#             form.save()
#             return redirect("dashboard:notes_list")
#     else:
#         form = DashboardNoteForm(instance=note)
#     return render(request, "dashboard/note_form.html", {"form": form, "note": note})


