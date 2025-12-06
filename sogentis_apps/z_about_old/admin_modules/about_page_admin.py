#about/admin_modules/about_page_admin.py
# about/admin_modules/about_page_admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from parler.admin import TranslatableAdmin, TranslatableTabularInline

from z_about_old.models.about_page import AboutPage
from z_about_old.models.mission_item import MissionItem
from z_about_old.models.vision_item import VisionItem
from z_about_old.models.value_item import ValueItem
from z_about_old.models.objective_item import ObjectiveItem
from z_about_old.models.team_member import TeamMember
from z_about_old.models.partner import Partner
from z_about_old.models.about_section import AboutSection


# ========= BASE INLINE ========= #
class BaseInline(TranslatableTabularInline):
    """
    Base commune pour les inlines multilingues avec aperçu d'image.
    """
    extra = 1
    ordering = ("order",)
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        image = getattr(obj, "image", None) or getattr(obj, "photo", None) or getattr(obj, "logo", None)
        if image:
            try:
                return format_html('<img src="{}" width="80" style="border-radius:8px;">', image.url)
            except ValueError:
                return "—"
        return "—"
    image_preview.short_description = _("Aperçu image")


# ========= SPECIFIC INLINES ========= #
class MissionInline(BaseInline):
    model = MissionItem
    fields = ("title", "description", "icon", "image", "order", "image_preview", "is_active")


class VisionInline(BaseInline):
    model = VisionItem
    fields = ("title", "description", "icon", "image", "order", "image_preview", "is_active")
    verbose_name = _("Vision")
    verbose_name_plural = _("Nos visions")


class ValueInline(BaseInline):
    model = ValueItem
    fields = ("title", "description", "icon", "image", "order", "image_preview", "is_active")
    verbose_name = _("Valeur")
    verbose_name_plural = _("Nos valeurs")


class ObjectiveInline(BaseInline):
    model = ObjectiveItem
    fields = ("title", "description", "order", "is_active")
    verbose_name = _("Objectif")
    verbose_name_plural = _("Nos objectifs")


class TeamMemberInline(TranslatableTabularInline):
    model = TeamMember
    extra = 1
    ordering = ("order",)
    fields = (
        "name", "role", "bio", "photo", "photo_preview",
        "email", "linkedin", "twitter", "order", "is_active"
    )
    readonly_fields = ("photo_preview",)

    def photo_preview(self, obj):
        if getattr(obj, "photo", None):
            try:
                return format_html('<img src="{}" width="80" height="80" style="border-radius:50%;">', obj.photo.url)
            except ValueError:
                return "—"
        return "—"
    photo_preview.short_description = _("Aperçu photo")


class PartnerInline(TranslatableTabularInline):
    model = Partner
    extra = 1
    ordering = ("order",)
    fields = ("name", "logo", "logo_preview", "website", "order", "is_active")
    readonly_fields = ("logo_preview",)

    def logo_preview(self, obj):
        if getattr(obj, "logo", None):
            try:
                return format_html('<img src="{}" width="100" style="object-fit:contain;">', obj.logo.url)
            except ValueError:
                return "—"
        return "—"
    logo_preview.short_description = _("Aperçu logo")


# ========= ABOUT PAGE ADMIN ========= #
# @admin.register(AboutPage)
class AboutPageAdmin(TranslatableAdmin):
    """
    Administration de la page À propos avec inlines pour missions, visions, valeurs, objectifs, équipe et partenaires.
    """
    list_display = ("get_title", "cover_photo_preview", "created_at", "updated_at")
    search_fields = ("translations__title",)
    readonly_fields = ("cover_photo_preview", "created_at", "updated_at")
    inlines = [
        MissionInline,
        VisionInline,
        ValueInline,
        ObjectiveInline,
        TeamMemberInline,
        PartnerInline,
    ]

    fieldsets = (
        (_("Informations principales"), {
            "fields": ("title", "content", "cover_photo", "cover_photo_preview"),
        }),
        (_("Métadonnées"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

    def get_title(self, obj):
        return obj.safe_translation_getter("title", any_language=True) or _("(Page)")
    get_title.short_description = _("Titre")

    def cover_photo_preview(self, obj):
        if getattr(obj, "cover_photo", None):
            try:
                return format_html('<img src="{}" width="150" style="border-radius:8px;">', obj.cover_photo.url)
            except ValueError:
                return "—"
        return "—"
    cover_photo_preview.short_description = _("Photo de couverture")






# #about/admin_modules/about_page_admin.py
# # about/admin_modules/about_page_admin.py
# from django.contrib import admin
# from django.utils.html import format_html
# from django.utils.translation import gettext_lazy as _
# from parler.admin import TranslatableAdmin, TranslatableTabularInline

# from about.models.about_page import AboutPage
# from about.models.mission_item import MissionItem
# from about.models.vision_item import VisionItem
# from about.models.value_item import ValueItem
# from about.models.objective_item import ObjectiveItem
# from about.models.team_member import TeamMember
# from about.models.partner import Partner
# from about.models.about_section import AboutSection


# # ========= BASE INLINE ========= #
# class BaseInline(TranslatableTabularInline):
#     """
#     Base commune pour les inlines multilingues avec aperçu d'image.
#     """
#     extra = 1
#     ordering = ("order",)
#     readonly_fields = ("image_preview",)

#     def image_preview(self, obj):
#         image = getattr(obj, "image", None) or getattr(obj, "photo", None) or getattr(obj, "logo", None)
#         if image:
#             try:
#                 return format_html('<img src="{}" width="80" style="border-radius:8px;">', image.url)
#             except ValueError:
#                 return "—"
#         return "—"
#     image_preview.short_description = _("Aperçu image")


# # ========= SPECIFIC INLINES ========= #
# class MissionInline(BaseInline):
#     model = MissionItem
#     fields = ("title", "description", "icon", "image", "order", "image_preview", "is_active")


# class VisionInline(BaseInline):
#     model = VisionItem
#     fields = ("title", "description", "icon", "image", "order", "image_preview", "is_active")
#     verbose_name = _("Vision")
#     verbose_name_plural = _("Nos visions")


# class ValueInline(BaseInline):
#     model = ValueItem
#     fields = ("title", "description", "icon", "image", "order", "image_preview", "is_active")
#     verbose_name = _("Valeur")
#     verbose_name_plural = _("Nos valeurs")


# class ObjectiveInline(BaseInline):
#     model = ObjectiveItem
#     fields = ("title", "description", "order", "is_active")
#     verbose_name = _("Objectif")
#     verbose_name_plural = _("Nos objectifs")


# class TeamMemberInline(TranslatableTabularInline):
#     model = TeamMember
#     extra = 1
#     ordering = ("order",)
#     fields = (
#         "name", "role", "bio", "photo", "photo_preview",
#         "email", "linkedin", "twitter", "order", "is_active"
#     )
#     readonly_fields = ("photo_preview",)

#     def photo_preview(self, obj):
#         if getattr(obj, "photo", None):
#             try:
#                 return format_html('<img src="{}" width="80" height="80" style="border-radius:50%;">', obj.photo.url)
#             except ValueError:
#                 return "—"
#         return "—"
#     photo_preview.short_description = _("Aperçu photo")


# class PartnerInline(TranslatableTabularInline):
#     model = Partner
#     extra = 1
#     ordering = ("order",)
#     fields = ("name", "logo", "logo_preview", "website", "order", "is_active")
#     readonly_fields = ("logo_preview",)

#     def logo_preview(self, obj):
#         if getattr(obj, "logo", None):
#             try:
#                 return format_html('<img src="{}" width="100" style="object-fit:contain;">', obj.logo.url)
#             except ValueError:
#                 return "—"
#         return "—"
#     logo_preview.short_description = _("Aperçu logo")


# # ========= ABOUT PAGE ADMIN ========= #
# # @admin.register(AboutPage)
# class AboutPageAdmin(TranslatableAdmin):
#     """
#     Administration de la page À propos avec inlines pour missions, visions, valeurs, objectifs, équipe et partenaires.
#     """
#     list_display = ("get_title", "cover_photo_preview", "created_at", "updated_at")
#     search_fields = ("translations__title",)
#     readonly_fields = ("cover_photo_preview", "created_at", "updated_at")
#     inlines = [
#         MissionInline,
#         VisionInline,
#         ValueInline,
#         ObjectiveInline,
#         TeamMemberInline,
#         PartnerInline,
#     ]

#     fieldsets = (
#         (_("Informations principales"), {
#             "fields": ("title", "content", "cover_photo", "cover_photo_preview"),
#         }),
#         (_("Métadonnées"), {
#             "fields": ("created_at", "updated_at"),
#             "classes": ("collapse",)
#         }),
#     )

#     def get_title(self, obj):
#         return obj.safe_translation_getter("title", any_language=True) or _("(Page)")
#     get_title.short_description = _("Titre")

#     def cover_photo_preview(self, obj):
#         if getattr(obj, "cover_photo", None):
#             try:
#                 return format_html('<img src="{}" width="150" style="border-radius:8px;">', obj.cover_photo.url)
#             except ValueError:
#                 return "—"
#         return "—"
#     cover_photo_preview.short_description = _("Photo de couverture")


# # ========= ABOUT SECTION ADMIN ========= #
# # @admin.register(AboutSection)
# class AboutSectionAdmin(TranslatableAdmin):
#     """
#     Administration indépendante des sections À propos.
#     """
#     list_display = ("title", "section_type", "order", "is_active", "created_at", "updated_at")
#     list_filter = ("section_type", "is_active")
#     search_fields = ("translations__title", "translations__content")
#     readonly_fields = ("created_at", "updated_at")







# #about/admin_modules/about_page_admin.py
# from django.contrib import admin
# from django.utils.html import format_html
# from django.utils.translation import gettext_lazy as _
# from parler.admin import TranslatableAdmin, TranslatableTabularInline

# from about.models.about_page import AboutPage
# from about.models.mission_item import MissionItem
# from about.models.vision_item import VisionItem
# from about.models.value_item import ValueItem
# from about.models.objective_item import ObjectiveItem
# from about.models.team_member import TeamMember
# from about.models.partner import Partner


# # ========= INLINES ========= #
# class MissionInline(TranslatableTabularInline):
#     model = MissionItem
#     extra = 1
#     ordering = ("order",)
#     fields = ("title", "description", "icon", "image", "order", "image_preview")
#     readonly_fields = ("image_preview",)

#     def image_preview(self, obj):
#         if obj.image:
#             return format_html('<img src="{}" width="80" style="border-radius:8px;">', obj.image.url)
#         return "—"
#     image_preview.short_description = _("Aperçu image")


# class VisionInline(MissionInline):
#     model = VisionItem
#     verbose_name = _("Vision")
#     verbose_name_plural = _("Nos visions")


# class ValueInline(MissionInline):
#     model = ValueItem
#     verbose_name = _("Valeur")
#     verbose_name_plural = _("Nos valeurs")


# class ObjectiveInline(MissionInline):
#     model = ObjectiveItem
#     verbose_name = _("Objectif")
#     verbose_name_plural = _("Nos objectifs")


# class TeamMemberInline(TranslatableTabularInline):
#     model = TeamMember
#     extra = 1
#     ordering = ("order",)
#     fields = ("name", "role", "bio", "photo", "photo_preview", "email", "linkedin", "twitter", "order", "is_active")
#     readonly_fields = ("photo_preview",)

#     def photo_preview(self, obj):
#         if obj.photo:
#             return format_html('<img src="{}" width="80" height="80" style="border-radius:50%;">', obj.photo.url)
#         return "—"
#     photo_preview.short_description = _("Aperçu photo")


# class PartnerInline(TranslatableTabularInline):
#     model = Partner
#     extra = 1
#     ordering = ("order",)
#     fields = ("name", "logo", "logo_preview", "website", "order", "is_active")
#     readonly_fields = ("logo_preview",)

#     def logo_preview(self, obj):
#         if obj.logo:
#             return format_html('<img src="{}" width="100" style="object-fit:contain;">', obj.logo.url)
#         return "—"
#     logo_preview.short_description = _("Aperçu logo")


# # ========= ABOUT PAGE ADMIN ========= #
# @admin.register(AboutPage)
# class AboutPageAdmin(TranslatableAdmin):
#     list_display = ("get_title", "cover_photo_preview", "created_at", "updated_at")
#     search_fields = ("translations__title",)
#     readonly_fields = ("cover_photo_preview", "created_at", "updated_at")
#     inlines = [MissionInline, VisionInline, ValueInline, ObjectiveInline, TeamMemberInline, PartnerInline]

#     fieldsets = (
#         (_("Informations principales"), {
#             "fields": ("title", "content", "cover_photo", "cover_photo_preview"),
#         }),
#         (_("Métadonnées"), {
#             "fields": ("created_at", "updated_at"),
#             "classes": ("collapse",)
#         }),
#     )

#     def get_title(self, obj):
#         return obj.safe_translation_getter("title", any_language=True)
#     get_title.short_description = _("Titre")

#     def cover_photo_preview(self, obj):
#         if obj.cover_photo:
#             return format_html('<img src="{}" width="150" style="border-radius:8px;">', obj.cover_photo.url)
#         return "—"
#     cover_photo_preview.short_description = _("Photo de couverture")






# # about/admin_modules/about_page_admin.py
# from django.contrib import admin
# from django.utils.translation import gettext_lazy as _
# from django.utils.html import format_html
# from parler.admin import TranslatableAdmin, TranslatableTabularInline

# # Import des modèles
# from about.models.about_page import AboutPage
# from about.models.team_member import TeamMember
# from about.models.mission_item import MissionItem
# from about.models.vision_item import VisionItem
# from about.models.value_item import ValueItem
# from about.models.objective_item import ObjectiveItem
# from about.models.partner import Partner
# from about.models.child import Child
# from about.models.mother import Mother


# # ===========================
# # 🔹 INLINES GÉNÉRIQUES
# # ===========================
# class BaseInline(TranslatableTabularInline):
#     extra = 1
#     fields = ("title", "description", "icon", "image", "image_preview", "order", "is_active")
#     readonly_fields = ("image_preview",)
#     ordering = ("order",)

#     def image_preview(self, obj):
#         """Affiche un aperçu de l'image si disponible."""
#         if getattr(obj, "image", None):
#             try:
#                 return format_html(
#                     '<img src="{}" width="80" height="80" style="object-fit:cover;border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,0.15);">',
#                     obj.image.url
#                 )
#             except ValueError:
#                 return "—"
#         return "—"
#     image_preview.short_description = _("Aperçu image")


# # ===========================
# # 🔹 INLINES SPÉCIFIQUES
# # ===========================
# class MissionInline(BaseInline):
#     model = MissionItem
#     verbose_name = _("Mission")
#     verbose_name_plural = _("Nos Missions")


# class VisionInline(BaseInline):
#     model = VisionItem
#     verbose_name = _("Vision")
#     verbose_name_plural = _("Nos Visions")


# class ValueInline(BaseInline):
#     model = ValueItem
#     verbose_name = _("Valeur")
#     verbose_name_plural = _("Nos Valeurs")


# class ObjectiveInline(BaseInline):
#     model = ObjectiveItem
#     verbose_name = _("Objectif")
#     verbose_name_plural = _("Nos Objectifs")


# class TeamMemberInline(TranslatableTabularInline):
#     model = TeamMember
#     extra = 1
#     fields = ("name", "role", "bio", "photo", "photo_preview", "email", "linkedin", "twitter", "order", "is_active")
#     readonly_fields = ("photo_preview",)
#     ordering = ("order",)

#     def photo_preview(self, obj):
#         if getattr(obj, "photo", None):
#             try:
#                 return format_html(
#                     '<img src="{}" width="80" height="80" style="border-radius:50%;object-fit:cover;box-shadow:0 1px 3px rgba(0,0,0,0.15);">',
#                     obj.photo.url
#                 )
#             except ValueError:
#                 return "—"
#         return "—"
#     photo_preview.short_description = _("Aperçu photo")


# class PartnerInline(TranslatableTabularInline):
#     model = Partner
#     extra = 1
#     fields = ("name", "logo", "logo_preview", "website", "order", "is_active")
#     readonly_fields = ("logo_preview",)
#     ordering = ("order",)

#     def logo_preview(self, obj):
#         if getattr(obj, "logo", None):
#             try:
#                 return format_html(
#                     '<img src="{}" width="100" height="50" style="object-fit:contain;box-shadow:0 1px 3px rgba(0,0,0,0.15);">',
#                     obj.logo.url
#                 )
#             except ValueError:
#                 return "—"
#         return "—"
#     logo_preview.short_description = _("Aperçu logo")


# # ===========================
# # 🔹 ADMIN DES ENFANTS ET MAMANS
# # ===========================
# @admin.register(Child)
# class ChildAdmin(admin.ModelAdmin):
#     list_display = ("name", "age", "gender", "is_active")
#     list_filter = ("is_active", "gender")
#     search_fields = ("name",)
#     fieldsets = (
#         (None, {
#             "fields": ("about_page", "name", "age", "gender", "photo", "story", "is_active")
#         }),
#     )


# @admin.register(Mother)
# class MotherAdmin(admin.ModelAdmin):
#     list_display = ("name", "profession", "is_active")
#     list_filter = ("is_active",)
#     search_fields = ("name", "profession")
#     fieldsets = (
#         (None, {
#             "fields": ("about_page", "name", "profession", "photo", "story", "is_active")
#         }),
#     )


# # ===========================
# # 🔹 ADMIN PRINCIPAL : ABOUT PAGE
# # ===========================
# @admin.register(AboutPage)
# class AboutPageAdmin(TranslatableAdmin):
#     """
#     Admin de la page 'À propos', avec gestion des sous-sections.
#     """
#     list_display = ("get_title", "cover_photo_preview", "created_at", "updated_at")
#     search_fields = ("translations__title", "translations__content")
#     readonly_fields = ("created_at", "updated_at", "cover_photo_preview")

#     inlines = [
#         MissionInline,
#         VisionInline,
#         ValueInline,
#         ObjectiveInline,
#         TeamMemberInline,
#         PartnerInline,
#     ]

#     fieldsets = (
#         (_("📰 Informations générales"), {
#             "fields": ("title", "content", "cover_photo", "cover_photo_preview"),
#         }),
#         (_("🕒 Métadonnées"), {
#             "fields": ("created_at", "updated_at"),
#             "classes": ("collapse",)
#         }),
#     )

#     def get_title(self, obj):
#         return obj.safe_translation_getter("title", any_language=True)
#     get_title.short_description = _("Titre")

#     def cover_photo_preview(self, obj):
#         if getattr(obj, "cover_photo", None):
#             try:
#                 return format_html(
#                     '<img src="{}" width="150" style="border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,0.15);">',
#                     obj.cover_photo.url
#                 )
#             except ValueError:
#                 return "—"
#         return "—"
#     cover_photo_preview.short_description = _("Photo de couverture")




# from django.contrib import admin
# from django.utils.translation import gettext_lazy as _
# from parler.admin import TranslatableAdmin, TranslatableTabularInline
# from django.utils.html import format_html

# from about.models.about_page import AboutPage
# from about.models.team_member import TeamMember
# from about.models.mission_item import MissionItem
# from about.models.vision_item import VisionItem
# from about.models.value_item import ValueItem
# from about.models.objective_item import ObjectiveItem
# from about.models.partner import Partner
# from about.models.child import Child
# from about.models.mother import Mother


# # ====== INLINES GÉNÉRIQUES ====== #
# class BaseInline(TranslatableTabularInline):
#     extra = 1
#     fields = ("title", "description", "icon", "image", "order", "image_preview")
#     readonly_fields = ("image_preview",)
#     ordering = ("order",)

#     def image_preview(self, obj):
#         if getattr(obj, "image", None):
#             return format_html(
#                 '<img src="{}" width="80" height="80" style="object-fit:cover;border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,0.15);">',
#                 obj.image.url
#             )
#         return "—"
#     image_preview.short_description = _("Aperçu image")


# # ====== INLINES SPÉCIFIQUES ====== #
# class MissionInline(BaseInline):
#     model = MissionItem
#     verbose_name = _("Mission")
#     verbose_name_plural = _("Nos Missions")


# class VisionInline(BaseInline):
#     model = VisionItem
#     verbose_name = _("Vision")
#     verbose_name_plural = _("Nos Visions")


# class ValueInline(BaseInline):
#     model = ValueItem
#     verbose_name = _("Valeur")
#     verbose_name_plural = _("Nos Valeurs")


# class ObjectiveInline(BaseInline):
#     model = ObjectiveItem
#     verbose_name = _("Objectif")
#     verbose_name_plural = _("Nos Objectifs")


# class TeamMemberInline(TranslatableTabularInline):
#     model = TeamMember
#     extra = 1
#     fields = ("name", "role", "bio", "photo", "photo_preview", "email", "linkedin", "twitter", "order", "is_active")
#     readonly_fields = ("photo_preview",)
#     ordering = ("order",)

#     def photo_preview(self, obj):
#         if obj.photo:
#             return format_html(
#                 '<img src="{}" width="80" height="80" style="border-radius:50%;object-fit:cover;box-shadow:0 1px 3px rgba(0,0,0,0.15);">',
#                 obj.photo.url
#             )
#         return "—"
#     photo_preview.short_description = _("Aperçu photo")


# class PartnerInline(TranslatableTabularInline):
#     model = Partner
#     extra = 1
#     fields = ("name", "logo", "logo_preview", "order", "website")
#     readonly_fields = ("logo_preview",)
#     ordering = ("order",)

#     def logo_preview(self, obj):
#         if obj.logo:
#             return format_html(
#                 '<img src="{}" width="80" height="50" style="object-fit:contain;box-shadow:0 1px 3px rgba(0,0,0,0.15);">',
#                 obj.logo.url
#             )
#         return "—"
#     logo_preview.short_description = _("Aperçu logo")


# # ====== ABOUT PAGE ADMIN ====== #
# # @admin.register(AboutPage)
# class AboutPageAdmin(TranslatableAdmin):
#     """
#     Admin de la page 'À propos', avec gestion complète des sections traduisibles.
#     """
#     list_display = ("get_title", "cover_photo_preview", "created_at", "updated_at")
#     search_fields = ("translations__title", "translations__content")
#     readonly_fields = ("created_at", "updated_at", "cover_photo_preview")
#     inlines = [
#         MissionInline,
#         VisionInline,
#         ValueInline,
#         ObjectiveInline,
#         TeamMemberInline,
#         PartnerInline,
#     ]

#     fieldsets = (
#         (_("📰 Informations générales"), {
#             "fields": ("title", "content", "cover_photo", "cover_photo_preview"),
#         }),
#         (_("🕒 Métadonnées"), {
#             "fields": ("created_at", "updated_at"),
#             "classes": ("collapse",)
#         }),
#     )

#     def get_title(self, obj):
#         return obj.safe_translation_getter("title", any_language=True)
#     get_title.short_description = _("Titre")

#     def cover_photo_preview(self, obj):
#         if obj.cover_photo:
#             return format_html(
#                 '<img src="{}" width="150" style="border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,0.15);">',
#                 obj.cover_photo.url
#             )
#         return "—"
#     cover_photo_preview.short_description = _("Photo de couverture")





# #about/admin_modules/about_page_admin.py
# from django.contrib import admin
# from django.utils.translation import gettext_lazy as _
# from parler.admin import TranslatableAdmin, TranslatableTabularInline
# from django.utils.html import format_html
# from ..models import MissionItem, VisionItem, ValueItem, ObjectiveItem
# from about.models.about_page import (
#     AboutPage
# )


# # ====== INLINES GÉNÉRIQUES ====== #
# class BaseInline(TranslatableTabularInline):
#     extra = 1
#     fields = ("title", "description", "icon", "image", "order", "image_preview")
#     readonly_fields = ("image_preview",)
#     ordering = ("order",)

#     def image_preview(self, obj):
#         if obj.image:
#             return format_html(
#                 '<img src="{}" width="80" height="80" style="object-fit:cover;border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,0.15);">',
#                 obj.image.url
#             )
#         return "—"
#     image_preview.short_description = "Aperçu image"


# class MissionInline(BaseInline):
#     model = MissionItem
#     verbose_name = "Mission"
#     verbose_name_plural = "Nos Missions"


# class VisionInline(BaseInline):
#     model = VisionItem
#     verbose_name = "Vision"
#     verbose_name_plural = "Nos Visions"


# class ValueInline(BaseInline):
#     model = ValueItem
#     verbose_name = "Valeur"
#     verbose_name_plural = "Nos Valeurs"


# class ObjectiveInline(BaseInline):
#     model = ObjectiveItem
#     verbose_name = "Objectif"
#     verbose_name_plural = "Nos Objectifs"


# # ====== ABOUT PAGE ADMIN ====== #
# #If you prefer to centralize all registrations in about/admin.py, then remove the decorator
# # @admin.register(AboutPage)
# class AboutPageAdmin(TranslatableAdmin):
#     """
#     Admin de la page 'À propos' avec gestion complète des sections :
#     Missions, Visions, Valeurs et Objectifs.
#     """
#     list_display = ("get_title", "cover_photo_preview", "created_at", "updated_at")
#     search_fields = ("translations__title", "translations__content")
#     readonly_fields = ("created_at", "updated_at", "cover_photo_preview")
#     inlines = [MissionInline, VisionInline, ValueInline, ObjectiveInline]

#     fieldsets = (
#         ("📰 Informations générales", {
#             "fields": ("title", "content", "cover_photo", "cover_photo_preview"),
#         }),
#         ("🕒 Métadonnées", {
#             "fields": ("created_at", "updated_at"),
#             "classes": ("collapse",)
#         }),
#     )

#     def get_title(self, obj):
#         return obj.safe_translation_getter("title", any_language=True)
#     get_title.short_description = "Titre"

#     def cover_photo_preview(self, obj):
#         if obj.cover_photo:
#             return format_html('<img src="{}" width="150" style="border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,0.15);">', obj.cover_photo.url)
#         return "—"
#     cover_photo_preview.short_description = "Photo de couverture"




# # about/admin/about_page_admin.py
# from django.contrib import admin
# from parler.admin import TranslatableAdmin, TranslatableTabularInline
# from django.utils.html import format_html
# from about.models.about_page import AboutPage, MissionItem, VisionItem


# class MissionInline(TranslatableTabularInline):
#     model = MissionItem
#     extra = 1
#     fields = ("title", "description", "icon", "image", "order", "image_preview")
#     readonly_fields = ("image_preview",)
#     ordering = ("order",)

#     def image_preview(self, obj):
#         if obj.image:
#             return format_html(
#                 '<img src="{}" width="80" height="80" style="object-fit:cover;border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,0.15);">',
#                 obj.image.url
#             )
#         return "—"
#     image_preview.short_description = "Aperçu image"


# class VisionInline(TranslatableTabularInline):
#     model = VisionItem
#     extra = 1
#     fields = ("title", "description", "icon", "image", "order", "image_preview")
#     readonly_fields = ("image_preview",)
#     ordering = ("order",)

#     def image_preview(self, obj):
#         if obj.image:
#             return format_html(
#                 '<img src="{}" width="80" height="80" style="object-fit:cover;border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,0.15);">',
#                 obj.image.url
#             )
#         return "—"
#     image_preview.short_description = "Aperçu image"


# @admin.register(AboutPage)
# class AboutPageAdmin(TranslatableAdmin):
#     """
#     Admin de la page 'À propos' avec sections dynamiques :
#     - Mission : liste d'items (texte, icône, photo)
#     - Vision : liste d'items (texte, icône, photo)
#     """
#     list_display = ("get_title", "cover_photo_preview", "created_at", "updated_at")
#     search_fields = ("translations__title", "translations__content")
#     readonly_fields = ("created_at", "updated_at", "cover_photo_preview")
#     inlines = [MissionInline, VisionInline]

#     fieldsets = (
#         ("📰 Informations générales", {
#             "fields": ("title", "content", "cover_photo", "cover_photo_preview"),
#         }),
#         ("🕒 Métadonnées", {
#             "fields": ("created_at", "updated_at"),
#             "classes": ("collapse",)
#         }),
#     )

#     def get_title(self, obj):
#         return obj.safe_translation_getter("title", any_language=True)
#     get_title.short_description = "Titre"

#     def cover_photo_preview(self, obj):
#         if obj.cover_photo:
#             return format_html('<img src="{}" width="150" style="border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,0.15);">', obj.cover_photo.url)
#         return "—"
#     cover_photo_preview.short_description = "Photo de couverture"




# # about/admin/about_page_admin.py
# from django.contrib import admin
# from parler.admin import TranslatableAdmin, TranslatableTabularInline
# from django.utils.html import format_html
# from about.models.about_page import AboutPage, MissionItem, VisionItem


# class MissionInline(TranslatableTabularInline):
#     model = MissionItem
#     extra = 1
#     fields = ("title", "description", "icon", "image", "order")
#     readonly_fields = ("image_preview",)

#     def image_preview(self, obj):
#         if obj.image:
#             return format_html('<img src="{}" width="80" height="80" style="object-fit:cover;border-radius:8px;">', obj.image.url)
#         return "—"
#     image_preview.short_description = "Aperçu"


# class VisionInline(TranslatableTabularInline):
#     model = VisionItem
#     extra = 1
#     fields = ("title", "description", "icon", "image", "order")
#     readonly_fields = ("image_preview",)

#     def image_preview(self, obj):
#         if obj.image:
#             return format_html('<img src="{}" width="80" height="80" style="object-fit:cover;border-radius:8px;">', obj.image.url)
#         return "—"
#     image_preview.short_description = "Aperçu"


# @admin.register(AboutPage)
# class AboutPageAdmin(TranslatableAdmin):
#     list_display = ("get_title", "cover_photo_preview", "created_at", "updated_at")
#     search_fields = ("translations__title", "translations__content")
#     readonly_fields = ("created_at", "updated_at", "cover_photo_preview")
#     fieldsets = (
#         ("Informations générales", {"fields": ("title", "content", "cover_photo", "cover_photo_preview")}),
#         ("Métadonnées", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
#     )
#     inlines = [MissionInline, VisionInline]

#     def get_title(self, obj):
#         return obj.safe_translation_getter("title", any_language=True)
#     get_title.short_description = "Titre"

#     def cover_photo_preview(self, obj):
#         if obj.cover_photo:
#             return format_html('<img src="{}" width="120" style="border-radius:8px;">', obj.cover_photo.url)
#         return "—"
#     cover_photo_preview.short_description = "Photo de couverture"





# # about/admin/about_page_admin.py
# from django.contrib import admin
# from parler.admin import TranslatableAdmin
# from about.models.about_page import AboutPage
# from django.utils.html import format_html

# @admin.register(AboutPage)
# class AboutPageAdmin(TranslatableAdmin):
#     list_display = ("get_title", "cover_photo_preview", "created_at", "updated_at")
#     search_fields = ("translations__title", "translations__content")
#     readonly_fields = ("created_at", "updated_at")
#     fieldsets = (
#         ("Infos générales", {"fields": ("title", "content", "cover_photo")}),
#         ("Mission & Vision", {"fields": ("mission", "vision"), "classes": ("collapse",)}),
#     )

#     def get_title(self, obj):
#         return obj.safe_translation_getter("title", any_language=True)
#     get_title.short_description = "Titre"

#     def cover_photo_preview(self, obj):
#         if obj.cover_photo:
#             return format_html('<img src="{}" width="120"/>', obj.cover_photo.url)
#         return "Pas de photo"
#     cover_photo_preview.short_description = "Photo de couverture"




# from django.contrib import admin
# from django.utils.translation import gettext_lazy as _
# from parler.admin import TranslatableAdmin
# from about.models.about_page import AboutPage  # ✅ Import direct pour éviter les circular imports

# @admin.register(AboutPage)
# class AboutPageAdmin(TranslatableAdmin):
#     list_display = ("get_title", "created_at", "updated_at")
#     search_fields = ("translations__title", "translations__content")
#     list_per_page = 20
#     readonly_fields = ("created_at", "updated_at")

#     fieldsets = (
#         ("Informations générales", {"fields": ("title", "content")}),
#         ("Mission & Vision", {"fields": ("mission", "vision"), "classes": ("collapse",)}),
#         ("Dates", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
#     )

#     def get_title(self, obj):
#         return obj.safe_translation_getter("title", any_language=True)
#     get_title.short_description = "Titre"







# from django.contrib import admin
# from django.utils.translation import gettext_lazy as _
# from about.models import AboutPage

# @admin.register(AboutPage)
# class AboutPageAdmin(admin.ModelAdmin):
#     list_display = ("title", "created_at", "updated_at")
#     search_fields = ("title", "content")
#     list_per_page = 20
#     fieldsets = (
#         (_("Informations générales"), {"fields": ("title", "content")}),
#         (_("Mission & Vision"), {"fields": ("mission", "vision"), "classes": ("collapse",)}),
#         (_("Dates"), {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
#     )
#     readonly_fields = ("created_at", "updated_at")
