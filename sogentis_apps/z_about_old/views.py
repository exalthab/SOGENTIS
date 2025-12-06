# about/views.py
"""
Vue centrale pour l’application 'about'
Chaque module de vue est importé depuis about/views/
Conforme à une architecture Django modulaire.
"""

from z_about_old.views.about_page_views import AboutPageListView, AboutPageDetailView
from z_about_old.views.about_section_views import AboutSectionListView
from z_about_old.views.objective_views import ObjectiveListView
from z_about_old.views.team_member_views import TeamMemberListView
from z_about_old.views.partner_views import PartnerListView
from z_about_old.views.child_views import ChildListView
from z_about_old.views.mother_views import MotherListView
from z_about_old.views.sponsor_views import SponsorListView



# from django.shortcuts import render, get_object_or_404
# from django.utils import timezone, translation
# from django.http import HttpResponse
# from .models import AboutPage, AboutSection, TeamMember, Partner, Child, Mother, Objective


# # =============================
# # PAGE PRINCIPALE "À propos"
# # =============================
# def index(request):
#     """Affiche la page publique 'À propos'"""
#     current_language = translation.get_language()

#     # =============================
#     # Chargement des données traduites
#     # =============================
#     page = AboutPage.objects.language(current_language).first()
#     sections = AboutSection.objects.language(current_language).all().order_by("order")
#     objectives = Objective.objects.language(current_language).filter(is_active=True).order_by("order")
#     team = TeamMember.objects.language(current_language).filter(is_active=True).order_by("order")
#     mothers = Mother.objects.language(current_language).filter(is_active=True)
#     partners = Partner.objects.language(current_language).filter(is_active=True).order_by("order")

#     # =============================
#     # Modèles non traduits
#     # =============================
#     children = Child.objects.filter(is_active=True).order_by("name")

#     # =============================
#     # Préparer les champs traduits pour les templates
#     # (cela évite les appels complexes dans les templates)
#     # =============================
#     if page:
#         page.title_trans = page.safe_translation_getter("title", any_language=True)
#         page.subtitle_trans = page.safe_translation_getter("subtitle", any_language=True)
#         page.content_trans = page.safe_translation_getter("content", any_language=True)
#         page.mission_trans = page.safe_translation_getter("mission", any_language=True)
#         page.vision_trans = page.safe_translation_getter("vision", any_language=True)

#     for section in sections:
#         section.title_trans = section.safe_translation_getter("title", any_language=True)
#         section.subtitle_trans = section.safe_translation_getter("subtitle", any_language=True)
#         section.content_trans = section.safe_translation_getter("content", any_language=True)

#     for member in team:
#         member.name_trans = member.safe_translation_getter("name", any_language=True)
#         member.role_trans = member.safe_translation_getter("role", any_language=True)
#         member.bio_trans = member.safe_translation_getter("bio", any_language=True)

#     for mother in mothers:
#         mother.name_trans = mother.safe_translation_getter("name", any_language=True)
#         mother.story_trans = mother.safe_translation_getter("story", any_language=True)

#     for partner in partners:
#         partner.name_trans = partner.safe_translation_getter("name", any_language=True)
#         partner.description_trans = partner.safe_translation_getter("description", any_language=True)

#     for objective in objectives:
#         objective.title_trans = objective.safe_translation_getter("title", any_language=True)
#         objective.description_trans = objective.safe_translation_getter("description", any_language=True)

#     # =============================
#     # Images par défaut
#     # =============================
#     for child in children:
#         child.photo_url = child.photo.url if child.photo else "/static/about/img/silhouette_child.png"
#     for mother in mothers:
#         mother.photo_url = mother.photo.url if mother.photo else "/static/about/img/silhouette_mother.png"
#     for member in team:
#         member.photo_url = member.photo.url if member.photo else "/static/about/img/default_team.png"
#     for partner in partners:
#         partner.logo_url = partner.logo.url if partner.logo else "/static/about/img/default_partner.png"

#     # =============================
#     # Vérifier si aucune donnée
#     # =============================
#     if not any([page, sections.exists(), objectives.exists(), team.exists(),
#                 children.exists(), mothers.exists(), partners.exists()]):
#         return HttpResponse("ℹ️ Aucune information 'À propos' n’a encore été enregistrée.")

#     # =============================
#     # Dernière mise à jour
#     # =============================
#     timestamps = []
#     if page and getattr(page, "updated_at", None):
#         timestamps.append(page.updated_at)
#     for queryset in [sections, objectives, team, children, mothers, partners]:
#         model_cls = queryset.model
#         if hasattr(model_cls, "updated_at") and queryset.exists():
#             try:
#                 timestamps.append(queryset.latest("updated_at").updated_at)
#             except model_cls.DoesNotExist:
#                 pass
#     latest_update = max(timestamps) if timestamps else None

#     # =============================
#     # CONTEXTE
#     # =============================
#     context = {
#         "page": page,
#         "sections": sections,
#         "objectives": objectives,
#         "team": team,
#         "children": children,
#         "mothers": mothers,
#         "partners": partners,
#         "latest_update": latest_update,
#     }

#     return render(request, "about/index.html", context)


# # =============================
# # UTILITAIRES
# # =============================
# def calculate_age(birth_date):
#     """Calcule l’âge à partir de la date de naissance"""
#     if not birth_date:
#         return None
#     today = timezone.now().date()
#     return today.year - birth_date.year - (
#         (today.month, today.day) < (birth_date.month, birth_date.day)
#     )


# # =============================
# # ENFANTS
# # =============================
# def children_list(request):
#     children = Child.objects.filter(is_active=True).order_by("name")
#     for child in children:
#         child.photo_url = child.photo.url if child.photo else "/static/about/img/silhouette_child.png"
#     return render(request, "about/children_list.html", {"children": children})


# def child_detail(request, pk):
#     child = get_object_or_404(Child, pk=pk, is_active=True)
#     child.photo_url = child.photo.url if child.photo else "/static/about/img/silhouette_child.png"
#     return render(request, "about/child_detail.html", {"child": child})


# def child_support_view(request, pk):
#     child = get_object_or_404(Child, pk=pk, is_active=True)
#     child.photo_url = child.photo.url if child.photo else "/static/about/img/silhouette_child.png"

#     donations = getattr(child, "donations", None)
#     if donations is not None:
#         donations = donations.select_related("sponsor").all()
#         total_funded = sum(d.amount for d in donations)
#     else:
#         donations, total_funded = [], 0

#     return render(request, "about/child_support.html", {
#         "child": child,
#         "donations": donations,
#         "total_funded": total_funded,
#     })


# # =============================
# # MAMANS
# # =============================
# def mother_detail(request, pk):
#     current_language = translation.get_language()
#     mother = get_object_or_404(
#         Mother.objects.language(current_language),
#         pk=pk,
#         is_active=True
#     )
#     mother.photo_url = mother.photo.url if mother.photo else "/static/about/img/silhouette_mother.png"
#     return render(request, "about/mother_detail.html", {"mother": mother})



# # about/views.py
# from django.shortcuts import render, get_object_or_404
# from django.utils import timezone, translation
# from django.http import HttpResponse
# from .models import AboutPage, AboutSection, TeamMember, Partner, Child, Mother, Objective


# # =============================
# # PAGE PRINCIPALE "À propos"
# # =============================
# def index(request):
#     """Affiche la page publique 'À propos'"""
#     current_language = translation.get_language()

#     # Modèles traduits
#     page = AboutPage.objects.language(current_language).first()
#     sections = AboutSection.objects.language(current_language).all().order_by("order")
#     objectives = Objective.objects.language(current_language).filter(is_active=True).order_by("order")
#     team = TeamMember.objects.language(current_language).filter(is_active=True).order_by("order")
#     mothers = Mother.objects.language(current_language).filter(is_active=True)
#     partners = Partner.objects.language(current_language).filter(is_active=True).order_by("order")

#     # Modèles non traduits
#     children = Child.objects.filter(is_active=True).order_by("name")

#     # Générer photo_url / logo_url pour les templates
#     for child in children:
#         child.photo_url = child.photo.url if child.photo else "/static/about/img/silhouette_child.png"
#     for mother in mothers:
#         mother.photo_url = mother.photo.url if mother.photo else "/static/about/img/silhouette_mother.png"
#     for member in team:
#         member.photo_url = member.photo.url if member.photo else "/static/about/img/default_team.png"
#     for partner in partners:
#         partner.logo_url = partner.logo.url if partner.logo else "/static/about/img/default_partner.png"

#     # Vérifier si aucune donnée n'existe
#     if not any([page, sections.exists(), objectives.exists(), team.exists(),
#                 children.exists(), mothers.exists(), partners.exists()]):
#         return HttpResponse("ℹ️ Aucune information 'À propos' n’a encore été enregistrée.")

#     # Dernière mise à jour
#     timestamps = []
#     if page and getattr(page, "updated_at", None):
#         timestamps.append(page.updated_at)
#     for queryset in [sections, objectives, team, children, mothers, partners]:
#         model_cls = queryset.model
#         if hasattr(model_cls, "updated_at") and queryset.exists():
#             try:
#                 timestamps.append(queryset.latest("updated_at").updated_at)
#             except model_cls.DoesNotExist:
#                 pass
#     latest_update = max(timestamps) if timestamps else None

#     context = {
#         "page": page,
#         "sections": sections,
#         "objectives": objectives,
#         "team": team,
#         "children": children,
#         "mothers": mothers,
#         "partners": partners,
#         "latest_update": latest_update,
#     }

#     return render(request, "about/index.html", context)


# # =============================
# # UTILITAIRES
# # =============================
# def calculate_age(birth_date):
#     """Calcule l’âge à partir de la date de naissance"""
#     if not birth_date:
#         return None
#     today = timezone.now().date()
#     return today.year - birth_date.year - (
#         (today.month, today.day) < (birth_date.month, birth_date.day)
#     )


# # =============================
# # ENFANTS
# # =============================
# def children_list(request):
#     children = Child.objects.filter(is_active=True).order_by("name")
#     for child in children:
#         child.photo_url = child.photo.url if child.photo else "/static/about/img/silhouette_child.png"
#     return render(request, "about/children_list.html", {"children": children})


# def child_detail(request, pk):
#     child = get_object_or_404(Child, pk=pk, is_active=True)
#     child.photo_url = child.photo.url if child.photo else "/static/about/img/silhouette_child.png"
#     return render(request, "about/child_detail.html", {"child": child})


# def child_support_view(request, pk):
#     child = get_object_or_404(Child, pk=pk, is_active=True)
#     child.photo_url = child.photo.url if child.photo else "/static/about/img/silhouette_child.png"

#     donations = getattr(child, "donations", None)
#     if donations is not None:
#         donations = donations.select_related("sponsor").all()
#         total_funded = sum(d.amount for d in donations)
#     else:
#         donations, total_funded = [], 0

#     return render(request, "about/child_support.html", {
#         "child": child,
#         "donations": donations,
#         "total_funded": total_funded,
#     })


# # =============================
# # MAMANS
# # =============================
# def mother_detail(request, pk):
#     current_language = translation.get_language()
#     mother = get_object_or_404(
#         Mother.objects.language(current_language),
#         pk=pk,
#         is_active=True
#     )
#     mother.photo_url = mother.photo.url if mother.photo else "/static/about/img/silhouette_mother.png"
#     return render(request, "about/mother_detail.html", {"mother": mother})




# # about/views.py
# from django.shortcuts import render, get_object_or_404
# from django.utils import timezone
# from django.http import HttpResponse
# from .models import AboutPage, AboutSection, TeamMember, Partner, Child, Mother, Objective

# # =============================
# # PAGE PRINCIPALE "À propos"
# # =============================
# def index(request):
#     """
#     Affiche la page publique 'À propos'
#     """
#     page = AboutPage.objects.first()
#     sections = AboutSection.objects.all().order_by("order")
#     objectives = Objective.objects.filter(is_active=True).order_by("order")
#     team = TeamMember.objects.all().order_by("order")
#     children = Child.objects.filter(is_active=True).order_by("name")
#     mothers = Mother.objects.filter(is_active=True).order_by("name")
#     partners = Partner.objects.all().order_by("order")

#     # Générer photo_url / logo_url pour les templates
#     for child in children:
#         child.photo_url = child.photo.url if child.photo else "/static/about/img/silhouette_child.png"
#     for mother in mothers:
#         mother.photo_url = mother.photo.url if mother.photo else "/static/about/img/silhouette_mother.png"
#     for member in team:
#         member.photo_url = member.photo.url if member.photo else "/static/about/img/default_team.png"
#     for partner in partners:
#         partner.logo_url = partner.logo.url if partner.logo else "/static/about/img/default_partner.png"

#     # Vérifier si aucune donnée n'existe
#     if not any([page, sections.exists(), objectives.exists(), team.exists(), children.exists(), mothers.exists(), partners.exists()]):
#         return HttpResponse("ℹ️ Aucune information 'À propos' n’a encore été enregistrée.")

#     # Dernière mise à jour
#     timestamps = []
#     if page and getattr(page, "updated_at", None):
#         timestamps.append(page.updated_at)
#     for queryset in [sections, objectives, team, children, mothers, partners]:
#         model_cls = queryset.model
#         if hasattr(model_cls, "updated_at") and queryset.exists():
#             try:
#                 timestamps.append(queryset.latest("updated_at").updated_at)
#             except model_cls.DoesNotExist:
#                 pass
#     latest_update = max(timestamps) if timestamps else None

#     context = {
#         "page": page,
#         "sections": sections,
#         "objectives": objectives,
#         "team": team,
#         "children": children,
#         "mothers": mothers,
#         "partners": partners,
#         "latest_update": latest_update,
#     }

#     return render(request, "about/index.html", context)


# # =============================
# # UTILITAIRES
# # =============================
# def calculate_age(birth_date):
#     """Calcule l’âge à partir de la date de naissance"""
#     if not birth_date:
#         return None
#     today = timezone.now().date()
#     return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


# # =============================
# # ENFANTS
# # =============================
# def children_list(request):
#     children = Child.objects.filter(is_active=True).order_by("name")
#     for child in children:
#         child.photo_url = child.photo.url if child.photo else "/static/about/img/silhouette_child.png"
#     return render(request, "about/children_list.html", {"children": children})


# def child_detail(request, pk):
#     child = get_object_or_404(Child, pk=pk, is_active=True)
#     child.photo_url = child.photo.url if child.photo else "/static/about/img/silhouette_child.png"
#     return render(request, "about/child_detail.html", {"child": child})


# def child_support_view(request, pk):
#     child = get_object_or_404(Child, pk=pk, is_active=True)
#     child.photo_url = child.photo.url if child.photo else "/static/about/img/silhouette_child.png"

#     donations = getattr(child, "donations", None)
#     if donations is not None:
#         donations = donations.select_related("sponsor").all()
#         total_funded = sum(d.amount for d in donations)
#     else:
#         donations, total_funded = [], 0

#     return render(request, "about/child_support.html", {
#         "child": child,
#         "donations": donations,
#         "total_funded": total_funded,
#     })


# # =============================
# # MAMANS
# # =============================
# def mother_detail(request, pk):
#     mother = get_object_or_404(Mother, pk=pk, is_active=True)
#     mother.photo_url = mother.photo.url if mother.photo else "/static/about/img/silhouette_mother.png"
#     return render(request, "about/mother_detail.html", {"mother": mother})



# # about/views.py
# from django.shortcuts import render, get_object_or_404
# from django.http import HttpResponse
# from django.utils import timezone
# from .models import AboutPage, AboutSection, TeamMember, Partner, Child, Mother, Objective


# # =============================
# # PAGE PRINCIPALE "À propos"
# # =============================
# def index(request):
#     """
#     Affiche la page publique 'À propos' avec :
#     - La page principale (mission, vision)
#     - Les sections dynamiques (histoire, valeurs, etc.)
#     - Les objectifs actifs
#     - Les membres de l'équipe
#     - Les enfants et mamans actifs
#     - Les partenaires
#     - La dernière mise à jour
#     """
#     page = AboutPage.objects.first()
#     sections = AboutSection.objects.all().order_by("order")
#     objectives = Objective.objects.filter(is_active=True).order_by("order")
#     team = TeamMember.objects.all().order_by("order")
#     children = Child.objects.filter(is_active=True).order_by("name")
#     mothers = Mother.objects.filter(is_active=True).order_by("name")
#     partners = Partner.objects.all().order_by("order")

#     if not any([page, sections.exists(), objectives.exists(), team.exists(), children.exists(), mothers.exists(), partners.exists()]):
#         return HttpResponse("ℹ️ Aucune information 'À propos' n’a encore été enregistrée.")

#     # 🔹 Détermination de la dernière mise à jour
#     timestamps = []

#     if page and getattr(page, "updated_at", None):
#         timestamps.append(page.updated_at)

#     for queryset in [sections, objectives, team, children, mothers, partners]:
#         model_cls = queryset.model
#         if hasattr(model_cls, "updated_at") and queryset.exists():
#             try:
#                 timestamps.append(queryset.latest("updated_at").updated_at)
#             except model_cls.DoesNotExist:
#                 pass

#     latest_update = max(timestamps) if timestamps else None

#     context = {
#         "page": page,
#         "sections": sections,
#         "objectives": objectives,
#         "team": team,
#         "children": children,
#         "mothers": mothers,
#         "partners": partners,
#         "latest_update": latest_update,
#     }

#     return render(request, "about/index.html", context)


# # =============================
# # UTILITAIRES
# # =============================
# def get_photo_url(obj, default_path):
#     """Retourne l’URL de la photo de l’objet ou une image par défaut."""
#     if getattr(obj, "photo", None):
#         try:
#             return obj.photo.url
#         except ValueError:
#             pass
#     return default_path


# def calculate_age(birth_date):
#     """Calcule l’âge en années à partir d’une date de naissance."""
#     if not birth_date:
#         return None
#     today = timezone.now().date()
#     return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


# # =============================
# # LISTE & DÉTAILS ENFANTS
# # =============================
# def children_list(request):
#     """Affiche la liste de tous les enfants actifs."""
#     children = Child.objects.filter(is_active=True).order_by("name")
#     for child in children:
#         child.photo_url = get_photo_url(child, "/static/about/img/silhouette_child.png")
#     return render(request, "about/children_list.html", {"children": children})


# def child_detail(request, pk):
#     """Affiche la page de détails d’un enfant avec son histoire complète."""
#     child = get_object_or_404(Child, pk=pk, is_active=True)
#     child.photo_url = get_photo_url(child, "/static/about/img/silhouette_child.png")
#     return render(request, "about/child_detail.html", {"child": child})


# def child_support_view(request, pk):
#     """
#     Page de soutien pour un enfant :
#     - photo à gauche
#     - infos identifiantes sous la photo
#     - description et historique des fonds à droite
#     """
#     child = get_object_or_404(Child, pk=pk, is_active=True)
#     child.photo_url = get_photo_url(child, "/static/about/img/silhouette_child.png")

#     donations = getattr(child, "donations", None)
#     if donations is not None:
#         donations = donations.select_related("sponsor").all()
#         total_funded = sum(d.amount for d in donations)
#     else:
#         donations, total_funded = [], 0

#     context = {
#         "child": child,
#         "donations": donations,
#         "total_funded": total_funded,
#     }
#     return render(request, "about/child_support.html", context)


# # =============================
# # DÉTAIL MAMAN
# # =============================
# def mother_detail(request, pk):
#     """Affiche la page de détails d’une maman."""
#     mother = get_object_or_404(Mother, pk=pk, is_active=True)
#     mother.photo_url = get_photo_url(mother, "/static/about/img/silhouette_mother.png")
#     return render(request, "about/mother_detail.html", {"mother": mother})




# #about/views.py
# from django.shortcuts import render, get_object_or_404
# from django.http import HttpResponse
# from django.utils import timezone
# from .models import AboutPage, AboutSection, TeamMember, Partner, Child, Mother, Objective


# # =============================
# # PAGE PRINCIPALE "À propos"
# # =============================
# def index(request):
#     """
#     Affiche la page publique 'À propos' avec :
#     - La page principale (mission, vision)
#     - Les sections dynamiques (histoire, valeurs, etc.)
#     - Les objectifs actifs
#     - Les membres de l'équipe
#     - Les enfants et mamans actifs
#     - Les partenaires
#     - La dernière mise à jour
#     """
#     page = AboutPage.objects.first()
#     sections = AboutSection.objects.all().order_by("order")
#     objectives = Objective.objects.filter(is_active=True).order_by("order")
#     team = TeamMember.objects.all().order_by("order")
#     children = Child.objects.filter(is_active=True).order_by("name")
#     mothers = Mother.objects.filter(is_active=True).order_by("name")
#     partners = Partner.objects.all().order_by("order")

#     # Vérifie qu’au moins un contenu existe
#     if not any([
#         page,
#         sections.exists(),
#         objectives.exists(),
#         team.exists(),
#         children.exists(),
#         mothers.exists(),
#         partners.exists(),
#     ]):
#         return HttpResponse("ℹ️ Aucune information 'À propos' n’a encore été enregistrée.")

#     # 🔹 Détermination de la dernière mise à jour
#     timestamps = []

#     if page and hasattr(page, "updated_at") and page.updated_at:
#         timestamps.append(page.updated_at)

#     for queryset in [sections, objectives, team, children, mothers, partners]:
#         model_cls = queryset.model
#         if hasattr(model_cls, "updated_at") and queryset.exists():
#             try:
#                 timestamps.append(queryset.latest("updated_at").updated_at)
#             except model_cls.DoesNotExist:
#                 pass

#     latest_update = max(timestamps) if timestamps else None

#     context = {
#         "page": page,
#         "sections": sections,
#         "objectives": objectives,
#         "team": team,
#         "children": children,
#         "mothers": mothers,
#         "partners": partners,
#         "latest_update": latest_update,
#     }

#     return render(request, "about/index.html", context)


# # =============================
# # UTILITAIRES
# # =============================
# def get_photo_url(obj, default_path):
#     """Retourne l’URL de la photo de l’objet ou une image par défaut."""
#     if getattr(obj, "photo", None):
#         try:
#             return obj.photo.url
#         except ValueError:
#             pass
#     return default_path


# def calculate_age(birth_date):
#     """Calcule l’âge en années à partir d’une date de naissance."""
#     if not birth_date:
#         return None
#     today = timezone.now().date()
#     return today.year - birth_date.year - (
#         (today.month, today.day) < (birth_date.month, birth_date.day)
#     )


# # =============================
# # LISTE & DÉTAILS ENFANTS
# # =============================
# def children_list(request):
#     children = Child.objects.filter(is_active=True).order_by("name")

#     # Ajoute uniquement l’URL de photo (l’âge est déjà calculé via le modèle)
#     for child in children:
#         child.photo_url = get_photo_url(child, "/static/about/img/silhouette_child.png")

#     return render(request, "about/children_list.html", {"children": children})


# def child_detail(request, pk):
#     child = get_object_or_404(Child, pk=pk, is_active=True)
#     child.photo_url = get_photo_url(child, "/static/about/img/silhouette_child.png")
#     return render(request, "about/child_detail.html", {"child": child})


# def child_support_view(request, pk):
#     """
#     Page de soutien pour un enfant :
#     - photo à gauche
#     - infos identifiantes sous la photo
#     - description et historique des fonds à droite
#     """
#     child = get_object_or_404(Child, pk=pk, is_active=True)
#     child.photo_url = get_photo_url(child, "/static/about/img/silhouette_child.png")

#     donations = getattr(child, "donations", None)
#     if donations is not None:
#         donations = donations.select_related("sponsor").all()
#         total_funded = sum(d.amount for d in donations)
#     else:
#         donations, total_funded = [], 0

#     context = {
#         "child": child,
#         "donations": donations,
#         "total_funded": total_funded,
#     }
#     return render(request, "about/child_support.html", context)


# # =============================
# # DÉTAIL MAMAN
# # =============================
# def mother_detail(request, pk):
#     mother = get_object_or_404(Mother, pk=pk, is_active=True)
#     mother.photo_url = get_photo_url(mother, "/static/about/img/silhouette_mother.png")
#     return render(request, "about/mother_detail.html", {"mother": mother})
