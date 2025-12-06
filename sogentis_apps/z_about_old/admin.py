# about/admin.py
from django.contrib import admin

# 🧩 Import des classes admin
from z_about_old.admin_modules.about_page_admin import AboutPageAdmin
from z_about_old.admin_modules.mission_admin import MissionItemAdmin
from z_about_old.admin_modules.vision_admin import VisionItemAdmin
from z_about_old.admin_modules.value_admin import ValueItemAdmin
from z_about_old.admin_modules.objective_admin import ObjectiveItemAdmin
from z_about_old.admin_modules.partner_admin import PartnerAdmin
from z_about_old.admin_modules.team_member_admin import TeamMemberAdmin
from z_about_old.admin_modules.child_admin import ChildAdmin
from z_about_old.admin_modules.mother_admin import MotherAdmin
from z_about_old.admin_modules.section_admin import AboutSectionAdmin

# 🧠 Import des modèles
from z_about_old.models.about_page import AboutPage
from z_about_old.models.mission_item import MissionItem
from z_about_old.models.vision_item import VisionItem
from z_about_old.models.value_item import ValueItem
from z_about_old.models.objective_item import ObjectiveItem
from z_about_old.models.partner import Partner
from z_about_old.models.team_member import TeamMember
from z_about_old.models.child import Child
from z_about_old.models.mother import Mother
from z_about_old.models.about_section import AboutSection


# ========= 🔒 Fonction d’enregistrement sécurisé ========= #
def safe_register(model, admin_class):
    """Évite les erreurs si le modèle est déjà enregistré."""
    try:
        if not admin.site.is_registered(model):
            admin.site.register(model, admin_class)
    except admin.sites.AlreadyRegistered:
        pass


# ========= ✅ Enregistrements ========= #
safe_register(AboutPage, AboutPageAdmin)
safe_register(MissionItem, MissionItemAdmin)
safe_register(VisionItem, VisionItemAdmin)
safe_register(ValueItem, ValueItemAdmin)
safe_register(ObjectiveItem, ObjectiveItemAdmin)
safe_register(Partner, PartnerAdmin)
safe_register(TeamMember, TeamMemberAdmin)
safe_register(Child, ChildAdmin)
safe_register(Mother, MotherAdmin)
safe_register(AboutSection, AboutSectionAdmin)











# #about/admin.py
# from django.contrib import admin
# from about.models.about_page import AboutPage
# from about.admin_modules.about_page_admin import AboutPageAdmin
# from about.admin_modules.objective_admin import ObjectiveItemAdmin
# from about.admin_modules.partner_admin import PartnerAdmin
# from about.admin_modules.child_admin import ChildAdmin
# from about.admin_modules.mother_admin import MotherAdmin
# from about.admin_modules.team_member_admin import TeamMemberAdmin
# from about.admin_modules.section_admin import AboutSectionAdmin
# from about.admin_modules.value_admin import ValueItemAdmin
# from about.admin_modules.vision_admin import VisionItemAdmin
# from about.admin_modules.mission_admin import MissionItemAdmin

# # 🧩 Import des modèles (nécessaires pour l’enregistrement)
# from about.models.mission_item import MissionItem
# from about.models.vision_item import VisionItem
# from about.models.value_item import ValueItem
# from about.models.objective_item import ObjectiveItem
# from about.models.partner import Partner
# from about.models.team_member import TeamMember
# from about.models.child import Child
# from about.models.mother import Mother
# from about.models.about_section import AboutSection


# # ========= ENREGISTREMENT DES ADMINS ========= #
# # On vérifie que le modèle n’est pas déjà enregistré avant de le faire

# def safe_register(model, admin_class):
#     """Évite les erreurs si le modèle est déjà enregistré."""
#     if not admin.site.is_registered(model):
#         admin.site.register(model, admin_class)


# safe_register(AboutPage, AboutPageAdmin)
# safe_register(MissionItem, MissionItemAdmin)
# safe_register(VisionItem, VisionItemAdmin)
# safe_register(ValueItem, ValueItemAdmin)
# safe_register(ObjectiveItem, ObjectiveItemAdmin)
# safe_register(Partner, PartnerAdmin)
# safe_register(TeamMember, TeamMemberAdmin)
# safe_register(Child, ChildAdmin)
# safe_register(Mother, MotherAdmin)
# safe_register(AboutSection, AboutSectionAdmin)






# about/admin.py
# """
# Import centralisé de tous les fichiers admin
# pour que Django les enregistre automatiquement.
# """
# # about/admin.py
# from django.contrib import admin
# from about.models.about_page import AboutPage
# from about.admin_modules.about_page_admin import AboutPageAdmin
# from about.admin_modules.objective_admin import ObjectiveAdmin
# from about.admin_modules.partner_admin import PartnerAdmin
# from about.admin_modules.child_admin import ChildAdmin
# from about.admin_modules.mother_admin import MotherAdmin
# from about.admin_modules.sponsor_admin import SponsorAdmin

# # admin.site.register(AboutPage, AboutPageAdmin)

# if not admin.site.is_registered(AboutPage):
#     admin.site.register(AboutPage, AboutPageAdmin)




# from about.admin_modules.about_page_admin import AboutPageAdmin
# from about.models.about_page import AboutPage

# # from about.admin_modules.about_section_admin import AboutSectionAdmin
# from about.admin_modules.objective_admin import ObjectiveAdmin
# # from about.admin_modules.team_member_admin import TeamMemberAdmin
# from about.admin_modules.partner_admin import PartnerAdmin
# from about.admin_modules.child_admin import ChildAdmin
# from about.admin_modules.mother_admin import MotherAdmin
# from about.admin_modules.sponsor_admin import SponsorAdmin
# # from about.admin_modules.child_donation_admin import ChildDonationAdmin


# admin.site.register(AboutPage, AboutPageAdmin)






# from .admin.about_page_admin import *
# from .admin.about_section_admin import *
# from .admin.objective_admin import *
# from .admin.team_member_admin import *
# from .admin.partner_admin import *
# from .admin.child_admin import *
# from .admin.mother_admin import *
# from .admin.sponsor_admin import *




# # about/admin.py
# from django.contrib import admin
# from django.utils.html import format_html
# from django.utils.translation import gettext_lazy as _
# from .models import (
#     AboutPage,
#     AboutSection,
#     TeamMember,
#     Partner,
#     Objective,
#     Child,
#     Mother,
#     Sponsor,
#     ChildDonation,
# )


# # ============================================================== #
# # 🌐 PAGE PRINCIPALE "À propos"
# # ============================================================== #
# @admin.register(AboutPage)
# class AboutPageAdmin(admin.ModelAdmin):
#     list_display = ("title", "created_at", "updated_at")
#     search_fields = ("title", "content")
#     list_per_page = 20
#     readonly_fields = ("created_at", "updated_at")

#     fieldsets = (
#         (_("Informations générales"), {"fields": ("title", "content")}),
#         (_("Mission & Vision"), {"fields": ("mission", "vision"), "classes": ("collapse",)}),
#         (_("Dates"), {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
#     )


# # ============================================================== #
# # 🧩 SECTIONS DYNAMIQUES
# # ============================================================== #
# @admin.register(AboutSection)
# class AboutSectionAdmin(admin.ModelAdmin):
#     list_display = ("title", "section_type", "order", "preview_image", "updated_at")
#     list_filter = ("section_type",)
#     search_fields = ("title", "content")
#     ordering = ("order",)
#     list_editable = ("order",)
#     readonly_fields = ("created_at", "updated_at")

#     fieldsets = (
#         (_("Contenu"), {"fields": ("title", "content", "section_type")}),
#         (_("Image"), {"fields": ("image",)}),
#         (_("Ordre & Dates"), {"fields": ("order", "created_at", "updated_at")}),
#     )

#     def preview_image(self, obj):
#         if obj.image:
#             return format_html(
#                 '<img src="{}" width="70" height="70" style="border-radius:8px;object-fit:cover;"/>',
#                 obj.image.url
#             )
#         return _("Aucune image")

#     preview_image.short_description = _("Aperçu")


# # ============================================================== #
# # 👥 ÉQUIPE
# # ============================================================== #
# @admin.register(TeamMember)
# class TeamMemberAdmin(admin.ModelAdmin):
#     list_display = ("name", "role", "order", "photo_preview", "updated_at")
#     search_fields = ("name", "role")
#     ordering = ("order",)
#     list_editable = ("order",)
#     readonly_fields = ("created_at", "updated_at")

#     fieldsets = (
#         (_("Informations personnelles"), {"fields": ("name", "role", "photo")}),
#         (_("Ordre & Dates"), {"fields": ("order", "created_at", "updated_at")}),
#     )

#     def photo_preview(self, obj):
#         if obj.photo:
#             return format_html(
#                 '<img src="{}" width="60" height="60" style="border-radius:50%;object-fit:cover;"/>',
#                 obj.photo.url
#             )
#         return _("Pas de photo")

#     photo_preview.short_description = _("Photo")


# # ============================================================== #
# # 🎯 OBJECTIFS
# # ============================================================== #
# @admin.register(Objective)
# class ObjectiveAdmin(admin.ModelAdmin):
#     list_display = ("title", "is_active", "order", "created_at")
#     list_editable = ("is_active", "order")
#     search_fields = ("title", "description")
#     ordering = ("order",)
#     list_filter = ("is_active",)
#     readonly_fields = ("created_at", "updated_at")

#     fieldsets = (
#         (_("Détails"), {"fields": ("title", "description")}),
#         (_("Affichage"), {"fields": ("is_active", "order")}),
#         (_("Dates"), {"fields": ("created_at", "updated_at")}),
#     )


# # ============================================================== #
# # 🤝 PARTENAIRES
# # ============================================================== #
# @admin.register(Partner)
# class PartnerAdmin(admin.ModelAdmin):
#     list_display = ("name", "website_link", "logo_preview", "order", "updated_at")
#     search_fields = ("name", "website")
#     ordering = ("order",)
#     list_editable = ("order",)
#     readonly_fields = ("created_at", "updated_at")

#     fieldsets = (
#         (_("Informations"), {"fields": ("name", "website", "logo")}),
#         (_("Affichage"), {"fields": ("order",)}),
#         (_("Dates"), {"fields": ("created_at", "updated_at")}),
#     )

#     def website_link(self, obj):
#         if obj.website:
#             return format_html('<a href="{}" target="_blank">{}</a>', obj.website, obj.website)
#         return _("Aucun site")

#     website_link.short_description = _("Site web")

#     def logo_preview(self, obj):
#         if obj.logo:
#             return format_html(
#                 '<img src="{}" width="70" height="70" style="object-fit:contain;"/>',
#                 obj.logo.url
#             )
#         return _("Pas de logo")

#     logo_preview.short_description = _("Logo")


# # ============================================================== #
# # 👶 ENFANTS
# # ============================================================== #
# @admin.register(Child)
# class ChildAdmin(admin.ModelAdmin):
#     list_display = ("name", "gender", "age", "school", "is_active", "photo_preview")
#     list_filter = ("gender", "is_active")
#     search_fields = ("name", "registration_number", "school")
#     list_editable = ("is_active",)
#     readonly_fields = ("created_at", "updated_at")

#     fieldsets = (
#         (_("Informations personnelles"), {
#             "fields": ("name", "gender", "photo", "registration_number", "date_of_birth")
#         }),
#         (_("École & Histoire"), {"fields": ("school", "short_story")}),
#         (_("Statut & Dates"), {"fields": ("is_active", "created_at", "updated_at")}),
#     )

#     def photo_preview(self, obj):
#         if obj.photo:
#             return format_html(
#                 '<img src="{}" width="60" height="60" style="border-radius:50%;object-fit:cover;"/>',
#                 obj.photo.url
#             )
#         return _("Pas de photo")

#     photo_preview.short_description = _("Photo")


# # ============================================================== #
# # 🤱 MAMANS
# # ============================================================== #
# @admin.register(Mother)
# class MotherAdmin(admin.ModelAdmin):
#     list_display = ("name", "is_active", "photo_preview", "created_at")
#     list_filter = ("is_active",)
#     search_fields = ("name", "registration_number")
#     list_editable = ("is_active",)
#     readonly_fields = ("created_at", "updated_at")

#     fieldsets = (
#         (_("Informations"), {"fields": ("name", "registration_number", "photo", "story")}),
#         (_("Statut & Dates"), {"fields": ("is_active", "created_at", "updated_at")}),
#     )

#     def photo_preview(self, obj):
#         if obj.photo:
#             return format_html(
#                 '<img src="{}" width="60" height="60" style="border-radius:50%;object-fit:cover;"/>',
#                 obj.photo.url
#             )
#         return _("Pas de photo")

#     photo_preview.short_description = _("Photo")


# # ============================================================== #
# # 💝 SPONSORS
# # ============================================================== #
# @admin.register(Sponsor)
# class SponsorAdmin(admin.ModelAdmin):
#     list_display = ("name", "email")
#     search_fields = ("name", "email")


# # ============================================================== #
# # 💸 DONS POUR ENFANTS
# # ============================================================== #
# @admin.register(ChildDonation)
# class ChildDonationAdmin(admin.ModelAdmin):
#     list_display = ("child", "sponsor_name", "amount", "date")
#     list_filter = ("date",)
#     search_fields = ("child__name", "sponsor__name")
#     ordering = ("-date",)
#     date_hierarchy = "date"

#     autocomplete_fields = ("child", "sponsor")

#     def sponsor_name(self, obj):
#         return obj.sponsor.name if obj.sponsor else _("Anonyme")

#     sponsor_name.short_description = _("Sponsor")




# #about/admin.py
# from django.contrib import admin
# from django.utils.html import format_html
# from django.utils.translation import gettext_lazy as _
# from .models import (
#     AboutPage,
#     AboutSection,
#     TeamMember,
#     Partner,
#     Objective,
#     Child,
#     Mother,
#     Sponsor,
#     ChildDonation,
# )


# # ==============================================================
# # 🌐 PAGE PRINCIPALE "À propos"
# # ==============================================================
# @admin.register(AboutPage)
# class AboutPageAdmin(admin.ModelAdmin):
#     list_display = ("title", "created_at", "updated_at")
#     search_fields = ("title", "content")
#     list_per_page = 20
#     fieldsets = (
#         (_("Informations générales"), {
#             "fields": ("title", "content"),
#         }),
#         (_("Mission & Vision"), {
#             "fields": ("mission", "vision"),
#             "classes": ("collapse",),
#         }),
#         (_("Dates"), {
#             "fields": ("created_at", "updated_at"),
#             "classes": ("collapse",),
#         }),
#     )
#     readonly_fields = ("created_at", "updated_at")


# # ==============================================================
# # 🧩 SECTIONS DYNAMIQUES
# # ==============================================================
# @admin.register(AboutSection)
# class AboutSectionAdmin(admin.ModelAdmin):
#     list_display = ("title", "section_type", "order", "preview_image", "updated_at")
#     list_filter = ("section_type",)
#     search_fields = ("title", "content")
#     ordering = ("order",)
#     list_editable = ("order",)
#     readonly_fields = ("created_at", "updated_at")
#     fieldsets = (
#         (_("Contenu"), {"fields": ("title", "content", "section_type")}),
#         (_("Image"), {"fields": ("image",)}),
#         (_("Ordre & Dates"), {"fields": ("order", "created_at", "updated_at")}),
#     )

#     def preview_image(self, obj):
#         if obj.image:
#             return format_html('<img src="{}" width="70" height="70" style="border-radius:8px;object-fit:cover;"/>', obj.image.url)
#         return _("Aucune image")
#     preview_image.short_description = _("Aperçu")


# # ==============================================================
# # 👥 ÉQUIPE
# # ==============================================================
# @admin.register(TeamMember)
# class TeamMemberAdmin(admin.ModelAdmin):
#     list_display = ("name", "role", "order", "photo_preview", "updated_at")
#     search_fields = ("name", "role")
#     ordering = ("order",)
#     list_editable = ("order",)
#     readonly_fields = ("created_at", "updated_at")
#     fieldsets = (
#         (_("Informations personnelles"), {"fields": ("name", "role", "photo")}),
#         (_("Ordre & Dates"), {"fields": ("order", "created_at", "updated_at")}),
#     )

#     def photo_preview(self, obj):
#         if obj.photo:
#             return format_html('<img src="{}" width="60" height="60" style="border-radius:50%;object-fit:cover;"/>', obj.photo.url)
#         return _("Pas de photo")
#     photo_preview.short_description = _("Photo")


# # ==============================================================
# # 🎯 OBJECTIFS
# # ==============================================================
# @admin.register(Objective)
# class ObjectiveAdmin(admin.ModelAdmin):
#     list_display = ("title", "is_active", "order", "created_at")
#     list_editable = ("is_active", "order")
#     search_fields = ("title", "description")
#     ordering = ("order",)
#     readonly_fields = ("created_at", "updated_at")
#     list_filter = ("is_active",)
#     fieldsets = (
#         (_("Détails"), {"fields": ("title", "description")}),
#         (_("Affichage"), {"fields": ("is_active", "order")}),
#         (_("Dates"), {"fields": ("created_at", "updated_at")}),
#     )


# # ==============================================================
# # 🤝 PARTENAIRES
# # ==============================================================
# @admin.register(Partner)
# class PartnerAdmin(admin.ModelAdmin):
#     list_display = ("name", "website_link", "logo_preview", "order", "updated_at")
#     search_fields = ("name", "website")
#     ordering = ("order",)
#     list_editable = ("order",)
#     readonly_fields = ("created_at", "updated_at")
#     fieldsets = (
#         (_("Informations"), {"fields": ("name", "website", "logo")}),
#         (_("Affichage"), {"fields": ("order",)}),
#         (_("Dates"), {"fields": ("created_at", "updated_at")}),
#     )

#     def website_link(self, obj):
#         if obj.website:
#             return format_html('<a href="{}" target="_blank">{}</a>', obj.website, obj.website)
#         return _("Aucun site")
#     website_link.short_description = _("Site web")

#     def logo_preview(self, obj):
#         if obj.logo:
#             return format_html('<img src="{}" width="70" height="70" style="object-fit:contain;"/>', obj.logo.url)
#         return _("Pas de logo")
#     logo_preview.short_description = _("Logo")


# # ==============================================================
# # 👶 ENFANTS
# # ==============================================================
# @admin.register(Child)
# class ChildAdmin(admin.ModelAdmin):
#     list_display = ("name", "gender", "age", "school", "is_active", "photo_preview")
#     list_filter = ("gender", "is_active")
#     search_fields = ("name", "registration_number", "school")
#     list_editable = ("is_active",)
#     readonly_fields = ("created_at", "updated_at")
#     fieldsets = (
#         (_("Informations personnelles"), {"fields": ("name", "gender", "photo", "registration_number", "date_of_birth")}),
#         (_("École & Histoire"), {"fields": ("school", "short_story")}),
#         (_("Statut & Dates"), {"fields": ("is_active", "created_at", "updated_at")}),
#     )

#     def photo_preview(self, obj):
#         if obj.photo:
#             return format_html('<img src="{}" width="60" height="60" style="border-radius:50%;object-fit:cover;"/>', obj.photo.url)
#         return _("Pas de photo")
#     photo_preview.short_description = _("Photo")


# # ==============================================================
# # 🤱 MAMANS
# # ==============================================================
# @admin.register(Mother)
# class MotherAdmin(admin.ModelAdmin):
#     list_display = ("name", "is_active", "photo_preview", "created_at")
#     list_filter = ("is_active",)
#     search_fields = ("name", "registration_number")
#     list_editable = ("is_active",)
#     readonly_fields = ("created_at", "updated_at")
#     fieldsets = (
#         (_("Informations"), {"fields": ("name", "registration_number", "photo", "story")}),
#         (_("Statut & Dates"), {"fields": ("is_active", "created_at", "updated_at")}),
#     )

#     def photo_preview(self, obj):
#         if obj.photo:
#             return format_html('<img src="{}" width="60" height="60" style="border-radius:50%;object-fit:cover;"/>', obj.photo.url)
#         return _("Pas de photo")
#     photo_preview.short_description = _("Photo")


# # ==============================================================
# # 💝 SPONSORS
# # ==============================================================
# @admin.register(Sponsor)
# class SponsorAdmin(admin.ModelAdmin):
#     list_display = ("name", "email")
#     search_fields = ("name", "email")


# # ==============================================================
# # 💸 DONS POUR ENFANTS
# # ==============================================================
# @admin.register(ChildDonation)
# class ChildDonationAdmin(admin.ModelAdmin):
#     list_display = ("child", "sponsor_name", "amount", "date")
#     list_filter = ("date",)
#     search_fields = ("child__name", "sponsor__name")
#     ordering = ("-date",)

#     def sponsor_name(self, obj):
#         return obj.sponsor.name if obj.sponsor else _("Anonyme")
#     sponsor_name.short_description = _("Sponsor")





# from django.contrib import admin
# from django.utils.html import format_html
# from django.utils.translation import gettext_lazy as _
# from .models import (
#     AboutPage,
#     AboutSection,
#     TeamMember,
#     Partner,
#     Child,
#     Sponsor,
#     ChildDonation,
#     Mother,
#     Objective,
# )

# from parler.admin import TranslatableAdmin


# # =============================
# # 🌐 PAGE PRINCIPALE "À propos"
# # =============================
# @admin.register(AboutPage)
# class AboutPageAdmin(admin.ModelAdmin):
#     list_display = ("title", "subtitle", "created_at", "updated_at")
#     search_fields = ("title", "subtitle", "content")
#     list_filter = ("created_at", "updated_at")
#     readonly_fields = ("created_at", "updated_at")
#     fieldsets = (
#         (_("Informations principales"), {"fields": ("title", "subtitle", "content")}),
#         (_("Mission & Vision"), {"fields": ("mission", "vision")}),
#         (_("Métadonnées"), {"fields": ("created_at", "updated_at")}),
#     )


# # =============================
# # 🧩 SECTIONS DYNAMIQUES
# # =============================
# @admin.register(AboutSection)
# class AboutSectionAdmin(admin.ModelAdmin):
#     list_display = ("title", "section_type", "order", "is_active", "preview_image")
#     list_filter = ("section_type", "is_active")
#     search_fields = ("title", "content")
#     list_editable = ("order", "is_active")
#     search_fields = ("translations__title", "translations__content")
#     readonly_fields = ("created_at", "updated_at", "preview_image")
#     ordering = ("order",)
#     fieldsets = (
#         (_("Informations générales"), {"fields": ("title", "subtitle", "content")}),
#         (_("Type et affichage"), {"fields": ("section_type", "order", "is_active")}),
#         (_("Image"), {"fields": ("image", "preview_image")}),
#         (_("Métadonnées"), {"fields": ("created_at", "updated_at")}),
#     )

#     def preview_image(self, obj):
#         if obj.image:
#             return format_html('<img src="{}" width="100" style="border-radius:8px;">', obj.image.url)
#         return _("(Aucune image)")
#     preview_image.short_description = _("Aperçu")


# # =============================
# # 👥 ÉQUIPE
# # =============================
# @admin.register(TeamMember)
# class TeamMemberAdmin(admin.ModelAdmin):
#     list_display = ("name", "role", "order", "is_active", "preview_photo")
#     list_editable = ("order", "is_active")
#     search_fields = ("name", "role")
#     readonly_fields = ("created_at", "updated_at", "preview_photo")
#     fieldsets = (
#         (_("Informations personnelles"), {"fields": ("name", "role", "bio")}),
#         (_("Photo et affichage"), {"fields": ("photo", "preview_photo", "order", "is_active")}),
#         (_("Métadonnées"), {"fields": ("created_at", "updated_at")}),
#     )

#     def preview_photo(self, obj):
#         if obj.photo:
#             return format_html('<img src="{}" width="80" style="border-radius:50%;">', obj.photo.url)
#         return _("(Aucune photo)")
#     preview_photo.short_description = _("Aperçu")


# # =============================
# # 🤝 PARTENAIRES
# # =============================
# @admin.register(Partner)
# class PartnerAdmin(admin.ModelAdmin):
#     list_display = ("name", "website_link", "order", "is_active", "preview_logo")
#     list_editable = ("order", "is_active")
#     search_fields = ("name", "description")
#     readonly_fields = ("created_at", "updated_at", "preview_logo")
#     fieldsets = (
#         (_("Informations"), {"fields": ("name", "description", "website")}),
#         (_("Logo et affichage"), {"fields": ("logo", "preview_logo", "order", "is_active")}),
#         (_("Métadonnées"), {"fields": ("created_at", "updated_at")}),
#     )

#     def preview_logo(self, obj):
#         if obj.logo:
#             return format_html('<img src="{}" width="100" style="border-radius:8px;">', obj.logo.url)
#         return _("(Aucun logo)")
#     preview_logo.short_description = _("Aperçu")

#     def website_link(self, obj):
#         if obj.website:
#             return format_html('<a href="{}" target="_blank">{}</a>', obj.website, _("Visiter"))
#         return _("Aucun lien")
#     website_link.short_description = _("Site web")


# # =============================
# # 👶 ENFANTS
# # =============================
# class ChildDonationInline(admin.TabularInline):
#     model = ChildDonation
#     extra = 0
#     readonly_fields = ("date",)
#     fields = ("sponsor", "amount", "date")
#     ordering = ("-date",)


# @admin.register(Child)
# class ChildAdmin(admin.ModelAdmin):
#     list_display = ("name", "gender", "age_display", "school", "is_active", "preview_photo")
#     list_filter = ("gender", "is_active")
#     search_fields = ("name", "registration_number", "school")
#     readonly_fields = ("created_at", "updated_at", "preview_photo", "age_display")
#     list_editable = ("is_active",)
#     inlines = [ChildDonationInline]
#     fieldsets = (
#         (_("Informations de base"), {"fields": ("name", "gender", "registration_number", "date_of_birth", "school")}),
#         (_("Histoire"), {"fields": ("short_story",)}),
#         (_("Photo"), {"fields": ("photo", "preview_photo")}),
#         (_("Statut et dates"), {"fields": ("is_active", "created_at", "updated_at")}),
#     )

#     def preview_photo(self, obj):
#         if obj.photo:
#             return format_html('<img src="{}" width="80" style="border-radius:8px;">', obj.photo.url)
#         return _("(Aucune photo)")
#     preview_photo.short_description = _("Aperçu")

#     def age_display(self, obj):
#         return f"{obj.age} ans" if obj.age else _("N/A")
#     age_display.short_description = _("Âge")


# # =============================
# # 🎗️ SPONSORS
# # =============================
# @admin.register(Sponsor)
# class SponsorAdmin(admin.ModelAdmin):
#     list_display = ("name", "email")
#     search_fields = ("name", "email")


# @admin.register(ChildDonation)
# class ChildDonationAdmin(admin.ModelAdmin):
#     list_display = ("child", "sponsor", "amount", "date")
#     list_filter = ("date",)
#     search_fields = ("child__name", "sponsor__name")
#     date_hierarchy = "date"
#     ordering = ("-date",)


# # =============================
# # 🤱 MAMANS
# # =============================
# @admin.register(Mother)
# class MotherAdmin(admin.ModelAdmin):
#     list_display = ("name", "registration_number", "is_active", "preview_photo")
#     list_editable = ("is_active",)
#     search_fields = ("name", "registration_number")
#     readonly_fields = ("created_at", "updated_at", "preview_photo")
#     fieldsets = (
#         (_("Informations"), {"fields": ("name", "registration_number", "story")}),
#         (_("Photo"), {"fields": ("photo", "preview_photo")}),
#         (_("Statut et dates"), {"fields": ("is_active", "created_at", "updated_at")}),
#     )

#     def preview_photo(self, obj):
#         if obj.photo:
#             return format_html('<img src="{}" width="80" style="border-radius:8px;">', obj.photo.url)
#         return _("(Aucune photo)")
#     preview_photo.short_description = _("Aperçu")


# # =============================
# # 🎯 OBJECTIFS
# # =============================
# @admin.register(Objective)
# class ObjectiveAdmin(admin.ModelAdmin):
#     list_display = ("title", "icon", "order", "is_active")
#     list_editable = ("order", "is_active")
#     search_fields = ("title", "description")
#     readonly_fields = ("created_at", "updated_at")
#     fieldsets = (
#         (_("Informations principales"), {"fields": ("title", "description", "icon")}),
#         (_("Affichage"), {"fields": ("order", "is_active")}),
#         (_("Métadonnées"), {"fields": ("created_at", "updated_at")}),
#     )



# from django.contrib import admin
# from django.utils.html import format_html
# from .models import AboutPage, AboutSection, TeamMember, Partner, Child, Mother, Objective

# # =============================
# # 🌐 PAGE PRINCIPALE "À propos"
# # =============================
# @admin.register(AboutPage)
# class AboutPageAdmin(admin.ModelAdmin):
#     list_display = ('title', 'created_at', 'mission_preview', 'vision_preview')
#     search_fields = ('title', 'content', 'mission', 'vision')
#     readonly_fields = ('created_at',)

#     fieldsets = (
#         (None, {'fields': ('title', 'content', 'mission', 'vision')}),
#         ('Dates', {'fields': ('created_at',)}),
#     )

#     def mission_preview(self, obj):
#         return (obj.mission[:60] + '...') if obj.mission else "—"
#     mission_preview.short_description = "Mission"

#     def vision_preview(self, obj):
#         return (obj.vision[:60] + '...') if obj.vision else "—"
#     vision_preview.short_description = "Vision"

#     class Media:
#         css = {'all': ('about/css/admin_custom.css',)}


# # =============================
# # 🧩 SECTIONS DYNAMIQUES
# # =============================
# @admin.register(AboutSection)
# class AboutSectionAdmin(admin.ModelAdmin):
#     list_display = ('title', 'section_type', 'order', 'image_preview')
#     list_filter = ('section_type',)
#     ordering = ('order',)
#     search_fields = ('title', 'content')

#     def image_preview(self, obj):
#         if obj.image:
#             return format_html(
#                 '<a href="{0}" target="_blank">'
#                 '<img src="{0}" class="admin-thumb" title="Cliquez pour agrandir"></a>',
#                 obj.image.url
#             )
#         return "—"
#     image_preview.short_description = "Aperçu"

#     class Media:
#         css = {'all': ('about/css/admin_custom.css',)}


# # =============================
# # 👥 ÉQUIPE
# # =============================
# @admin.register(TeamMember)
# class TeamMemberAdmin(admin.ModelAdmin):
#     list_display = ('photo_preview', 'name', 'role', 'order')
#     ordering = ('order',)
#     search_fields = ('name', 'role')

#     def photo_preview(self, obj):
#         if obj.photo:
#             return format_html(
#                 '<a href="{0}" target="_blank">'
#                 '<img src="{0}" class="admin-thumb" title="Cliquez pour agrandir"></a>',
#                 obj.photo.url
#             )
#         return "—"
#     photo_preview.short_description = "Photo"

#     class Media:
#         css = {'all': ('about/css/admin_custom.css',)}


# # =============================
# # 🤝 PARTENAIRES
# # =============================
# @admin.register(Partner)
# class PartnerAdmin(admin.ModelAdmin):
#     list_display = ('logo_preview', 'name', 'website', 'order')
#     ordering = ('order',)
#     search_fields = ('name',)

#     def logo_preview(self, obj):
#         if obj.logo:
#             return format_html(
#                 '<a href="{0}" target="_blank">'
#                 '<img src="{0}" class="admin-thumb" title="Cliquez pour agrandir"></a>',
#                 obj.logo.url
#             )
#         return "—"
#     logo_preview.short_description = "Logo"

#     class Media:
#         css = {'all': ('about/css/admin_custom.css',)}


# # =============================
# # 👶 ENFANTS
# # =============================
# @admin.register(Child)
# class ChildAdmin(admin.ModelAdmin):
#     list_display = ('photo_preview', 'name', 'registration_number', 'school', 'age_display', 'short_story_preview', 'is_active')
#     list_filter = ('is_active',)
#     search_fields = ('name', 'registration_number', 'school')
#     ordering = ('name',)
#     readonly_fields = ('age_display', 'created_at')

#     fieldsets = (
#         (None, {'fields': ('photo', 'name', 'gender', 'registration_number', 'date_of_birth', 'school', 'short_story', 'is_active')}),
#         ('Informations système', {'fields': ('created_at', 'age_display')}),
#     )

#     def photo_preview(self, obj):
#         url = obj.photo.url if obj.photo else (
#             '/static/about/img/default_female.png' if obj.gender == 'F' else '/static/about/img/default_male.png'
#         )
#         return format_html(
#             '<a href="{0}" target="_blank">'
#             '<img src="{0}" style="width:45px; height:45px; border-radius:50%; object-fit:cover;" title="Cliquez pour agrandir"/>'
#             '</a>',
#             url
#         )
#     photo_preview.short_description = "Photo"

#     def age_display(self, obj):
#         return obj.age if hasattr(obj, 'age') else "—"
#     age_display.short_description = "Âge"

#     def short_story_preview(self, obj):
#         return (obj.short_story[:50] + '...') if obj.short_story else "—"
#     short_story_preview.short_description = "Petite histoire"

#     class Media:
#         css = {'all': ('about/css/admin_custom.css',)}


# # =============================
# # 🤱 MAMANS
# # =============================
# @admin.register(Mother)
# class MotherAdmin(admin.ModelAdmin):
#     list_display = ('photo_preview', 'name', 'registration_number', 'age_display', 'short_story_preview', 'is_active')
#     list_filter = ('is_active',)
#     search_fields = ('name', 'registration_number')
#     ordering = ('name',)
#     readonly_fields = ('age_display', 'created_at')

#     def photo_preview(self, obj):
#         url = obj.photo.url if obj.photo else '/static/about/img/default_female.png'
#         return format_html(
#             '<a href="{0}" target="_blank">'
#             '<img src="{0}" class="admin-thumb" title="Cliquez pour agrandir"/></a>',
#             url
#         )
#     photo_preview.short_description = "Photo"

#     def age_display(self, obj):
#         return obj.age if hasattr(obj, 'age') else "—"
#     age_display.short_description = "Âge"

#     def short_story_preview(self, obj):
#         return (obj.short_story[:50] + '...') if obj.short_story else "—"
#     short_story_preview.short_description = "Petite histoire"

#     class Media:
#         css = {'all': ('about/css/admin_custom.css',)}


# # =============================
# # 🎯 OBJECTIFS
# # =============================
# @admin.register(Objective)
# class ObjectiveAdmin(admin.ModelAdmin):
#     list_display = ('title', 'description_preview', 'order', 'is_active')
#     list_filter = ('is_active',)
#     search_fields = ('title', 'description')
#     ordering = ('order',)

#     def description_preview(self, obj):
#         return (obj.description[:60] + '...') if obj.description else "—"
#     description_preview.short_description = "Description"

#     class Media:
#         css = {'all': ('about/css/admin_custom.css',)}



# from django.contrib import admin
# from django.utils.html import format_html
# from .models import AboutPage, AboutSection, TeamMember, Partner, Child, Mother, Objective
# from django.utils.timezone import now

# # =============================
# # 🌐 PAGE PRINCIPALE "À propos"
# # =============================
# @admin.register(AboutPage)
# class AboutPageAdmin(admin.ModelAdmin):
#     list_display = ('title', 'created_at', 'mission_preview', 'vision_preview')
#     search_fields = ('title', 'content', 'mission', 'vision')
#     readonly_fields = ('created_at',)

#     fieldsets = (
#         (None, {'fields': ('title', 'content', 'mission', 'vision')}),
#         ('Dates', {'fields': ('created_at',)}),
#     )

#     def mission_preview(self, obj):
#         return (obj.mission[:60] + '...') if obj.mission else "—"
#     mission_preview.short_description = "Mission"

#     def vision_preview(self, obj):
#         return (obj.vision[:60] + '...') if obj.vision else "—"
#     vision_preview.short_description = "Vision"

#     class Media:
#         css = {'all': ('about/css/admin_custom.css',)}


# # =============================
# # 🧩 SECTIONS DYNAMIQUES
# # =============================
# @admin.register(AboutSection)
# class AboutSectionAdmin(admin.ModelAdmin):
#     list_display = ('title', 'section_type', 'order', 'image_preview')
#     list_filter = ('section_type',)
#     ordering = ('order',)
#     search_fields = ('title', 'content')

#     def image_preview(self, obj):
#         if obj.image:
#             return format_html(
#                 '<a href="{0}" target="_blank">'
#                 '<img src="{0}" class="admin-thumb" title="Cliquez pour agrandir"></a>',
#                 obj.image.url
#             )
#         return "—"
#     image_preview.short_description = "Aperçu"

#     class Media:
#         css = {'all': ('about/css/admin_custom.css',)}


# # =============================
# # 👥 ÉQUIPE
# # =============================
# @admin.register(TeamMember)
# class TeamMemberAdmin(admin.ModelAdmin):
#     list_display = ('photo_preview', 'name', 'role', 'order')
#     ordering = ('order',)
#     search_fields = ('name', 'role')

#     def photo_preview(self, obj):
#         if obj.photo:
#             return format_html(
#                 '<a href="{0}" target="_blank">'
#                 '<img src="{0}" class="admin-thumb" title="Cliquez pour agrandir"></a>',
#                 obj.photo.url
#             )
#         return "—"
#     photo_preview.short_description = "Photo"

#     class Media:
#         css = {'all': ('about/css/admin_custom.css',)}


# # =============================
# # 🤝 PARTENAIRES
# # =============================
# @admin.register(Partner)
# class PartnerAdmin(admin.ModelAdmin):
#     list_display = ('logo_preview', 'name', 'website', 'order')
#     ordering = ('order',)
#     search_fields = ('name',)

#     def logo_preview(self, obj):
#         if obj.logo:
#             return format_html(
#                 '<a href="{0}" target="_blank">'
#                 '<img src="{0}" class="admin-thumb" title="Cliquez pour agrandir"></a>',
#                 obj.logo.url
#             )
#         return "—"
#     logo_preview.short_description = "Logo"

#     class Media:
#         css = {'all': ('about/css/admin_custom.css',)}


# # =============================
# # 👶 ENFANTS
# # =============================
# @admin.register(Child)
# class ChildAdmin(admin.ModelAdmin):
#     list_display = ('photo_preview', 'name', 'registration_number', 'school', 'age', 'short_story_preview', 'is_active')
#     list_filter = ('is_active',)
#     search_fields = ('name', 'registration_number', 'school')
#     ordering = ('name',)
#     readonly_fields = ('age', 'created_at')

#     fieldsets = (
#         (None, {'fields': ('photo', 'name', 'gender', 'registration_number', 'date_of_birth', 'school', 'short_story', 'is_active')}),
#         ('Informations système', {'fields': ('created_at', 'age')}),
#     )

#     def photo_preview(self, obj):
#         url = obj.photo.url if obj.photo else (
#             '/static/about/img/default_female.png' if obj.gender == 'F' else '/static/about/img/default_male.png'
#         )
#         return format_html(
#             '<a href="{0}" target="_blank">'
#             '<img src="{0}" style="width:45px; height:45px; border-radius:50%; object-fit:cover;" title="Cliquez pour agrandir"/>'
#             '</a>',
#             url
#         )
#     photo_preview.short_description = "Photo"

#     def age(self, obj):
#         return obj.age  # L'attribut `age` doit être défini dans le modèle Child
#     age.short_description = "Âge"

#     def short_story_preview(self, obj):
#         return (obj.short_story[:50] + '...') if obj.short_story else "—"
#     short_story_preview.short_description = "Petite histoire"

#     class Media:
#         css = {'all': ('about/css/admin_custom.css',)}


# # =============================
# # 🤱 MAMANS
# # =============================
# @admin.register(Mother)
# class MotherAdmin(admin.ModelAdmin):
#     list_display = ('photo_preview', 'name', 'registration_number', 'age', 'short_story_preview', 'is_active')
#     list_filter = ('is_active',)
#     search_fields = ('name', 'registration_number')
#     ordering = ('name',)
#     readonly_fields = ('age', 'created_at')

#     def photo_preview(self, obj):
#         url = obj.photo.url if obj.photo else (
#             '/static/about/img/default_female.png'
#         )
#         return format_html(
#             '<a href="{0}" target="_blank">'
#             '<img src="{0}" class="admin-thumb" title="Cliquez pour agrandir"/></a>',
#             url
#         )
#     photo_preview.short_description = "Photo"

#     def age(self, obj):
#         if getattr(obj, 'date_of_birth', None):
#             return obj.age  # L'attribut `age` doit être défini dans le modèle Mother
#         return "—"
#     age.short_description = "Âge"

#     def short_story_preview(self, obj):
#         return (obj.short_story[:50] + '...') if obj.short_story else "—"
#     short_story_preview.short_description = "Petite histoire"

#     class Media:
#         css = {'all': ('about/css/admin_custom.css',)}


# # =============================
# # 🎯 OBJECTIFS
# # =============================
# @admin.register(Objective)
# class ObjectiveAdmin(admin.ModelAdmin):
#     list_display = ('title', 'description_preview', 'order', 'is_active')
#     list_filter = ('is_active',)
#     search_fields = ('title', 'description')
#     ordering = ('order',)

#     def description_preview(self, obj):
#         return (obj.description[:60] + '...') if obj.description else "—"
#     description_preview.short_description = "Description"

#     class Media:
#         css = {'all': ('about/css/admin_custom.css',)}

