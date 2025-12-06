# documents/views.py

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import ListView, CreateView, DetailView
from django.http import FileResponse
import os

from .models import Document


class ToggleDocumentVisibilityView(View):
    """Bascule la visibilité d'un document (public ↔ privé)."""
    
    @method_decorator(login_required)
    def post(self, request, pk):
        document = get_object_or_404(Document, pk=pk)

        if document.author != request.user:
            messages.error(request, "Vous n'êtes pas autorisé à modifier ce document.")
            return redirect(document.get_absolute_url())

        document.is_public = not document.is_public
        document.save()

        visibility = "public" if document.is_public else "privé"
        messages.success(request, f"Le document est maintenant {visibility}.")

        return redirect(request.META.get("HTTP_REFERER") or reverse("documents:list"))


class DocumentListView(ListView):
    """Affiche les documents accessibles à l'utilisateur (publics + privés s'il est l'auteur)."""
    
    model = Document
    template_name = "documents/document_list.html"
    context_object_name = "documents"

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated:
            return Document.objects.filter(Q(is_public=True) | Q(author=user)).order_by("-created_at")

        return Document.objects.filter(is_public=True).order_by("-created_at")


class DocumentCreateView(LoginRequiredMixin, CreateView):
    """Permet à un utilisateur authentifié de créer un nouveau document."""

    model = Document
    fields = ["title", "description", "file", "is_public"]
    template_name = "documents/document_form.html"
    success_url = reverse_lazy("documents:list")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_form(self):
        form = super().get_form()
        form.fields["is_public"].initial = True  # Le document est public par défaut
        return form


class DocumentArchiveView(LoginRequiredMixin, ListView):
    """Affiche les documents privés de l'utilisateur connecté."""
    
    model = Document
    template_name = "documents/document_archive.html"
    context_object_name = "documents"

    def get_queryset(self):
        return Document.objects.filter(is_public=False, author=self.request.user).order_by("-created_at")


class DocumentDetailView(DetailView):
    """Affiche un document s’il est public ou s’il appartient à l'utilisateur connecté."""

    model = Document
    template_name = "documents/document_detail.html"
    context_object_name = "document"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user

        if obj.is_public or (user.is_authenticated and obj.author == user):
            return obj

        raise Http404("Document privé ou inexistant.")


def search_documents(request):
    """Permet de rechercher des documents par titre ou description."""

    query = request.GET.get("q", "").strip()
    documents = Document.objects.none()

    if query:
        documents = Document.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

        if request.user.is_authenticated:
            documents = documents.filter(Q(is_public=True) | Q(author=request.user))
        else:
            documents = documents.filter(is_public=True)

    return render(request, "documents/search_results.html", {
        "query": query,
        "documents": documents,
    })

@login_required
def download_document(request, pk):
    document = get_object_or_404(Document, pk=pk)

    # Autorisation
    if not document.is_public and document.author != request.user:
        raise Http404("Document privé")

    if not document.file:
        raise Http404("Fichier introuvable")

    # Compter le téléchargement
    document.download_count += 1
    document.save(update_fields=["download_count"])

    # Envoyer le fichier
    file_path = document.file.path
    return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))











# #/documents/views.py
# from django.views.generic import ListView, CreateView, DetailView
# from .models import Document
# from django.urls import reverse_lazy
# from django.urls import reverse
# from django.http import Http404
# from django.db.models import Q
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render, redirect, get_object_or_404
# from django.utils.decorators import method_decorator
# from django.views import View
# from django.contrib import messages

# class ToggleDocumentVisibilityView(View):
#     @method_decorator(login_required)
#     def post(self, request, pk):
#         document = get_object_or_404(Document, pk=pk)

#         if document.author != request.user:
#             messages.error(request, "Vous n'êtes pas autorisé à modifier ce document.")
#             return redirect(document.get_absolute_url())

#         document.is_public = not document.is_public
#         document.save()
#         visibility = "public" if document.is_public else "privé"
#         messages.success(request, f"Le document est maintenant {visibility}.")
#         return redirect(request.META.get("HTTP_REFERER", reverse("documents:list")))

# class DocumentListView(ListView):
#     model = Document
#     template_name = "documents/document_list.html"
#     context_object_name = "documents"

#     def get_queryset(self):
#         user = self.request.user
#         if user.is_authenticated:
#             return Document.objects.filter(
#                 Q(is_public=True) | Q(author=user)
#             ).order_by("-created_at")
#         return Document.objects.filter(is_public=True).order_by("-created_at")


# class DocumentCreateView(CreateView):
#     model = Document
#     fields = ["title", "description", "file", "is_public"]
#     template_name = "documents/document_form.html"
#     success_url = reverse_lazy("documents:list")

#     def form_valid(self, form):
#         if self.request.user.is_authenticated:
#             form.instance.author = self.request.user
#         return super().form_valid(form)

#     def get_form(self):
#         form = super().get_form()
#         form.fields["is_public"].initial = True  # toujours public par défaut
#         return form

# class DocumentArchiveView(ListView):
#     model = Document
#     template_name = "documents/document_archive.html"
#     context_object_name = "documents"

#     def get_queryset(self):
#         user = self.request.user
#         if user.is_authenticated:
#             return Document.objects.filter(
#                 Q(is_public=False), Q(author=user)
#             ).order_by("-created_at")
#         # utilisateur non connecté → accès interdit
#         return Document.objects.none()

# class DocumentDetailView(DetailView):
#     model = Document
#     template_name = "documents/document_detail.html"
#     context_object_name = "document"

#     def get_object(self, queryset=None):
#         obj = super().get_object(queryset)
#         user = self.request.user

#         if obj.is_public:
#             return obj
#         elif user.is_authenticated and obj.author == user:
#             return obj
#         else:
#             raise Http404("Document privé ou inexistant.")
        
# def search_documents(request):
#     query = request.GET.get("q", "").strip()
#     documents = []

#     if query:
#         documents = Document.objects.filter(
#             Q(title__icontains=query) | Q(description__icontains=query)
#         )

#         # Filtrer selon l'utilisateur
#         if request.user.is_authenticated:
#             documents = documents.filter(
#                 Q(is_public=True) | Q(author=request.user)
#             )
#         else:
#             documents = documents.filter(is_public=True)

#     return render(request, "documents/search_results.html", {
#         "query": query,
#         "documents": documents
#     })