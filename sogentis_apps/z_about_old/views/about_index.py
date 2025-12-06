# about/views/about_index.py
from django.shortcuts import render
from django.utils.translation import get_language
from django.db.models import Sum, Prefetch
from z_about_old.models.about_page import AboutPage
from z_about_old.models.mission_item import MissionItem
from z_about_old.models.vision_item import VisionItem
from z_about_old.models.value_item import ValueItem
from z_about_old.models.objective_item import ObjectiveItem
from z_about_old.models.team_member import TeamMember
from z_about_old.models.partner import Partner
from z_about_old.models.child import Child
from z_about_old.models.mother import Mother


def about_index_view(request):
    """
    Vue publique pour la page 'À propos'.
    Récupère AboutPage + sections dynamiques optimisées pour l'affichage.
    """
    lang = get_language()

    # Récupération optimisée de la page principale "À propos"
    about_page = (
        AboutPage.objects
        .prefetch_related(
            Prefetch("missions", queryset=MissionItem.objects.order_by("order")),
            Prefetch("visions", queryset=VisionItem.objects.order_by("order")),
            Prefetch("values", queryset=ValueItem.objects.order_by("order")),
            Prefetch("objectives", queryset=ObjectiveItem.objects.order_by("order")),
        )
        .first()
    )

    # Si aucune page "À propos" n’existe encore
    if not about_page:
        return render(request, "about/about_index.html", {
            "missions": [],
            "visions": [],
            "values": [],
            "objectives": [],
            "about_page": None,
            "team": [],
            "children": [],
            "mothers": [],
            "partners": [],
            "stats": {},
            "latest_update": None,
        })

    # === SECTIONS PRINCIPALES ===
    missions = about_page.missions.all()
    visions = about_page.visions.all()
    values = about_page.values.all()
    objectives = about_page.objectives.all()

    # === ÉQUIPE ===
    team = TeamMember.objects.filter(is_active=True).order_by("order")
    for member in team:
        member.photo_url = getattr(member.photo, "url", "/static/about/img/default_team.png")

    # === ENFANTS ===
    children = (
        Child.objects.filter(is_active=True)
        .prefetch_related("donations")
        .order_by("name")[:8]
    )

    for child in children:
        child.photo_url = getattr(child.photo, "url", "/static/about/img/silhouette_child.png")
        total_funded = child.donations.aggregate(total=Sum("amount"))["total"] or 0
        target = getattr(child, "target_amount", 0) or 0
        child.total_funded = total_funded
        child.target_amount = target
        child.funded_pct = int((total_funded / target) * 100) if target else 0

    # === MAMANS ===
    mothers = Mother.objects.filter(is_active=True).order_by("name")[:8]
    for mom in mothers:
        mom.photo_url = getattr(mom.photo, "url", "/static/about/img/silhouette_mother.png")

    # === PARTENAIRES ===
    partners = Partner.objects.filter(is_active=True).order_by("order")
    for partner in partners:
        partner.logo_url = getattr(partner.logo, "url", "/static/about/img/default_partner.png")

    # === STATISTIQUES ===
    stats = {
        "missions": missions.count(),
        "visions": visions.count(),
        "values": values.count(),
        "objectives": objectives.count(),
        "team": team.count(),
        "partners": partners.count(),
        "children": len(children),
        "mothers": len(mothers),
    }

    # === DERNIÈRE MISE À JOUR ===
    dates = [
        getattr(about_page, "updated_at", None) or getattr(about_page, "created_at", None)
    ] + [
        getattr(obj, "updated_at", None) or getattr(obj, "created_at", None)
        for obj in list(missions) + list(visions) + list(values) + list(objectives)
    ]
    latest_update = max((d for d in dates if d is not None), default=None)

    # === CONTEXTE FINAL ===
    context = {
        "lang": lang,
        "about_page": about_page,
        "missions": missions,
        "visions": visions,
        "values": values,
        "objectives": objectives,
        "team": team,
        "children": children,
        "mothers": mothers,
        "partners": partners,
        "stats": stats,
        "latest_update": latest_update,
    }

    return render(request, "about/about_index.html", context)





# # about/views/about_index.py
# from django.shortcuts import render
# from django.utils.translation import get_language
# from django.db.models import Sum, Prefetch
# from about.models.about_page import AboutPage
# from about.models.mission_item import MissionItem
# from about.models.vision_item import VisionItem
# from about.models.value_item import ValueItem
# from about.models.objective_item import ObjectiveItem
# from about.models.team_member import TeamMember
# from about.models.partner import Partner
# from about.models.child import Child
# from about.models.mother import Mother

# def about_index_view(request):
#     """
#     Vue publique pour la page 'À propos'.
#     Récupère AboutPage + sections dynamiques optimisées pour l'affichage.
#     """
#     lang = get_language()

#     # Récupère la page "À propos" avec préfetch des sous-items
#     about_page = (
#         AboutPage.objects
#         .prefetch_related(
#             Prefetch("missions", queryset=MissionItem.objects.order_by("order")),
#             Prefetch("visions", queryset=VisionItem.objects.order_by("order")),
#             Prefetch("values", queryset=ValueItem.objects.order_by("order")),
#             Prefetch("objectives", queryset=ObjectiveItem.objects.filter(), to_attr="prefetched_objectives"),
#         )
#         .first()
#     )

#     # Defaults si pas de page
#     if not about_page:
#         context = {"missions": [], "visions": [], "values": [], "objectives": [], "about_page": None}
#         return render(request, "about/about_index.html", context)

#     # Sections (utilisation des related_name depuis AboutPage)
#     missions = about_page.missions.all()
#     visions = about_page.visions.all()
#     values = about_page.values.all()
#     objectives = about_page.objectives.filter()  # tu peux .filter(is_active=True) si champ présent

#     # Équipe
#     team = TeamMember.objects.filter(is_active=True).order_by("order")
#     for m in team:
#         m.photo_url = m.photo.url if getattr(m, "photo", None) else "/static/about/img/default_team.png"

#     # Enfants : préfetch donations et calcul total financé
#     children_qs = (
#         Child.objects.filter(is_active=True)
#         .prefetch_related("donations")
#         .order_by("name")[:8]
#     )
#     children = list(children_qs)
#     for c in children:
#         c.photo_url = c.photo.url if getattr(c, "photo", None) else "/static/about/img/silhouette_child.png"
#         c.total_funded = c.donations.aggregate(total=Sum("amount"))["total"] or 0
#         c.target_amount = getattr(c, "target_amount", None) or 0
#         c.funded_pct = int((c.total_funded / c.target_amount) * 100) if c.target_amount else 0

#     # Mamans
#     mothers = Mother.objects.filter(is_active=True).order_by("name")[:8]
#     for mom in mothers:
#         mom.photo_url = mom.photo.url if getattr(mom, "photo", None) else "/static/about/img/silhouette_mother.png"

#     # Partenaires
#     partners = Partner.objects.filter(is_active=True).order_by("order")
#     for p in partners:
#         p.logo_url = p.logo.url if getattr(p, "logo", None) else "/static/about/img/default_partner.png"

#     # Statistiques simples
#     stats = {
#         "num_missions": missions.count(),
#         "num_visions": visions.count(),
#         "num_values": values.count(),
#         "num_objectives": objectives.count(),
#         "num_team": team.count(),
#         "num_partners": partners.count(),
#     }

#     # Dernière mise à jour (approx) — correction pour ignorer None
#     dates = [
#         getattr(about_page, "updated_at", None) or getattr(about_page, "created_at", None)
#     ] + [
#         getattr(item, "updated_at", None) or getattr(item, "created_at", None)
#         for item in list(missions) + list(visions) + list(values) + list(objectives)
#     ]
#     dates = [d for d in dates if d is not None]
#     latest_update = max(dates) if dates else None

#     context = {
#         "lang": lang,
#         "about_page": about_page,
#         "missions": missions,
#         "visions": visions,
#         "values": values,
#         "objectives": objectives,
#         "team": team,
#         "children": children,
#         "mothers": mothers,
#         "partners": partners,
#         "stats": stats,
#         "latest_update": latest_update,
#     }

#     return render(request, "about/about_index.html", context)





# # about/views/about_index.py
# from django.shortcuts import render
# from django.utils.translation import get_language
# from about.models.about_page import AboutPage
# from about.models.mission_item import MissionItem
# from about.models.vision_item import VisionItem
# from about.models.value_item import ValueItem
# from about.models.objective_item import ObjectiveItem


# def about_index_view(request):
#     """
#     Vue multilingue pour la page 'À propos de nous'.
#     Récupère la page principale et toutes les sections traduites.
#     """
#     language = get_language()
#     about_page = AboutPage.objects.active_translations(language_code=language).first()

#     missions = MissionItem.objects.active_translations(language_code=language).order_by("order")
#     visions = VisionItem.objects.active_translations(language_code=language).order_by("order")
#     values = ValueItem.objects.active_translations(language_code=language).order_by("order")
#     objectives = ObjectiveItem.objects.active_translations(language_code=language).order_by("order")

#     context = {
#         "about_page": about_page,
#         "missions": missions,
#         "visions": visions,
#         "values": values,
#         "objectives": objectives,
#     }
#     return render(request, "about/about_index.html", context)




# #about/views/about_index.py
# from django.contrib import admin
# from parler.admin import TranslatableAdmin, TranslatableTabularInline
# from django.utils.html import format_html
# from django.shortcuts import render
# from about.models.about_page import AboutPage
# from about.models.mission_item import MissionItem
# from about.models.vision_item import VisionItem
# from about.models.value_item import ValueItem
# from about.models.objective_item import ObjectiveItem


# # ========== Inline communs pour cartes ==========
# class BaseCardInline(TranslatableTabularInline):
#     """Inline de base avec aperçu image + icône."""
#     extra = 1
#     fields = ("title", "description", "icon", "image", "order")
#     readonly_fields = ("image_preview",)
#     ordering = ("order",)

#     def image_preview(self, obj):
#         if obj.image:
#             return format_html(
#                 '<img src="{}" width="80" height="80" style="object-fit:cover;border-radius:8px;">',
#                 obj.image.url,
#             )
#         return "—"
#     image_preview.short_description = "Aperçu visuel"


# class MissionInline(BaseCardInline):
#     model = MissionItem
#     verbose_name = "Mission"
#     verbose_name_plural = "Missions"


# class VisionInline(BaseCardInline):
#     model = VisionItem
#     verbose_name = "Vision"
#     verbose_name_plural = "Visions"


# class ValueInline(BaseCardInline):
#     model = ValueItem
#     verbose_name = "Valeur"
#     verbose_name_plural = "Valeurs"


# class ObjectiveInline(BaseCardInline):
#     model = ObjectiveItem
#     verbose_name = "Objectif"
#     verbose_name_plural = "Objectifs"


# # ========== Administration principale ==========
# # @admin.register(AboutPage)
# class AboutPageAdmin(TranslatableAdmin):
#     list_display = ("get_title", "cover_photo_preview", "created_at", "updated_at")
#     search_fields = ("translations__title", "translations__content")
#     readonly_fields = ("created_at", "updated_at", "cover_photo_preview")

#     fieldsets = (
#         ("Informations générales", {
#             "fields": ("title", "content", "cover_photo", "cover_photo_preview"),
#         }),
#         ("Métadonnées", {
#             "fields": ("created_at", "updated_at"),
#             "classes": ("collapse",),
#         }),
#     )

#     inlines = [MissionInline, VisionInline, ValueInline, ObjectiveInline]

#     # ========== Méthodes utilitaires ==========
#     def get_title(self, obj):
#         return obj.safe_translation_getter("title", any_language=True)
#     get_title.short_description = "Titre"

#     def cover_photo_preview(self, obj):
#         if obj.cover_photo:
#             return format_html(
#                 '<img src="{}" width="120" style="border-radius:8px;">',
#                 obj.cover_photo.url,
#             )
#         return "—"
#     cover_photo_preview.short_description = "Photo de couverture"


# def about_index_view(request):
#     about_page = AboutPage.objects.first()
#     return render(request, "about/index.html", {"about_page": about_page})






# # about/views/about_index.py
# from django.shortcuts import render, get_object_or_404
# from django.utils.translation import get_language, gettext_lazy as _
# from django.db.models import Sum, Prefetch

# from about.models.about_page import AboutPage
# from about.models.about_section import AboutSection
# from about.models.objective import Objective
# from about.models.team_member import TeamMember
# from about.models.partner import Partner
# from about.models.child import Child
# from about.models.mother import Mother
# from about.models.sponsor import Sponsor


# def about_index_view(request):
#     """
#     Vue multilingue optimisée pour la page publique 'À propos de nous'.
#     Compatible avec django-parler + fallback FR si traduction absente.
#     """

#     lang = get_language()

#     # Sécurité : certaines requêtes échouent si pas de traduction enregistrée
#     def safe_translated_queryset(model):
#         try:
#             return model.objects.language(lang)
#         except Exception:
#             # Fallback sur toutes les langues disponibles
#             return model.objects.all()

#     # Page principale
#     about_page = safe_translated_queryset(AboutPage).first()

#     # Sections (Mission, Vision, Historique, etc.)
#     sections = safe_translated_queryset(AboutSection).order_by("order")

#     # Objectifs actifs
#     objectives = safe_translated_queryset(Objective).filter(is_active=True).order_by("order")

#     # Équipe
#     team = TeamMember.objects.filter(is_active=True).order_by("order")
#     for member in team:
#         member.photo_url = member.photo.url if member.photo else "/static/about/img/default_team.png"

#     # Enfants
#     children = (
#         Child.objects.filter(is_active=True)
#         .prefetch_related(Prefetch("donations"))
#         .order_by("name")[:8]
#     )
#     for child in children:
#         child.photo_url = child.photo.url if child.photo else "/static/about/img/silhouette_child.png"
#         child.total_funded = child.donations.aggregate(total=Sum("amount"))["total"] or 0

#     # Mamans
#     mothers = Mother.objects.filter(is_active=True).order_by("name")[:8]
#     for mother in mothers:
#         mother.photo_url = mother.photo.url if mother.photo else "/static/about/img/silhouette_mother.png"

#     # Partenaires
#     partners = Partner.objects.filter(is_active=True).order_by("order")
#     for partner in partners:
#         partner.logo_url = partner.logo.url if partner.logo else "/static/about/img/default_partner.png"

#     # Sponsors récents
#     sponsors = Sponsor.objects.all().order_by("-created_at")[:6]

#     context = {
#         "page_title": _("À propos de nous"),
#         "about_page": about_page,
#         "sections": sections,
#         "objectives": objectives,
#         "team": team,
#         "children": children,
#         "mothers": mothers,
#         "partners": partners,
#         "sponsors": sponsors,
#         "lang": lang,
#     }

#     return render(request, "about/about_index.html", context)









# # about/views/about_index.py
# from django.shortcuts import render
# from django.utils.translation import get_language, gettext_lazy as _
# from django.db.models import Sum, Prefetch
# from parler.models import TranslatableModel
# from about.models import (
#     AboutPage, AboutSection, Objective,
#     TeamMember, Partner, Child, Mother, Sponsor
# )


# def about_index_view(request):
#     """
#     Vue multilingue optimisée pour la page publique 'À propos de nous'.
#     Compatible avec django-parler + fallback FR si traduction absente.
#     """

#     lang = get_language()

#     # Sécurité : certaines requêtes échouent si pas de traduction enregistrée
#     def safe_translated_queryset(model):
#         try:
#             return model.objects.language(lang)
#         except Exception:
#             # Fallback sur toutes les langues disponibles
#             return model.objects.all()

#     # Page principale
#     about_page = safe_translated_queryset(AboutPage).first()

#     # Sections (Mission, Vision, Historique, etc.)
#     sections = safe_translated_queryset(AboutSection).order_by("order")

#     # Objectifs actifs
#     objectives = safe_translated_queryset(Objective).filter(is_active=True).order_by("order")

#     # Équipe
#     team = TeamMember.objects.filter(is_active=True).order_by("order")
#     for member in team:
#         member.photo_url = member.photo.url if member.photo else "/static/about/img/default_team.png"

#     # Enfants
#     children = (
#         Child.objects.filter(is_active=True)
#         .prefetch_related(Prefetch("donations"))
#         .order_by("name")[:8]
#     )
#     for child in children:
#         child.photo_url = child.photo.url if child.photo else "/static/about/img/silhouette_child.png"
#         child.total_funded = child.donations.aggregate(total=Sum("amount"))["total"] or 0

#     # Mamans
#     mothers = Mother.objects.filter(is_active=True).order_by("name")[:8]
#     for mother in mothers:
#         mother.photo_url = mother.photo.url if mother.photo else "/static/about/img/silhouette_mother.png"

#     # Partenaires
#     partners = Partner.objects.filter(is_active=True).order_by("order")
#     for partner in partners:
#         partner.logo_url = partner.logo.url if partner.logo else "/static/about/img/default_partner.png"

#     # Sponsors récents
#     sponsors = Sponsor.objects.all().order_by("-created_at")[:6]

#     context = {
#         "page_title": _("À propos de nous"),
#         "about_page": about_page,
#         "sections": sections,
#         "objectives": objectives,
#         "team": team,
#         "children": children,
#         "mothers": mothers,
#         "partners": partners,
#         "sponsors": sponsors,
#         "lang": lang,
#     }

#     return render(request, "about/about_index.html", context)
