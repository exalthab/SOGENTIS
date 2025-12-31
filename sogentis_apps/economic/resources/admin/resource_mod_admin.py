# economic/resources/admin/resource_mod_admin.py
from django.contrib import admin
from parler.admin import TranslatableAdmin

from ..models import ResourceMod, ResourceDocument


class ResourceDocumentInline(admin.TabularInline):
    model = ResourceDocument
    extra = 0
    fields = ("title", "file", "is_public", "created_at")
    readonly_fields = ("created_at",)


@admin.register(ResourceMod)
class ResourceModAdmin(TranslatableAdmin):
    list_display = ("_title", "category", "slug", "is_published", "created_at")
    list_filter = ("is_published", "created_at", "category")
    search_fields = ("translations__title", "slug")
    ordering = ("-created_at",)
    inlines = (ResourceDocumentInline,)  # ✅ tuple recommandé

    def _title(self, obj):
        return obj.safe_translation_getter("title", any_language=True)

    _title.short_description = "Titre"





# # economic/resources/admin/resource_mod_admin.py
# from django.contrib import admin
# from parler.admin import TranslatableAdmin

# from ..models import ResourceMod, ResourceDocument


# class ResourceDocumentInline(admin.TabularInline):
#     model = ResourceDocument
#     extra = 0
#     fields = ("title", "file", "is_public", "created_at")
#     readonly_fields = ("created_at",)


# @admin.register(ResourceMod)
# class ResourceModAdmin(TranslatableAdmin):
#     list_display = ("_title", "category", "slug", "is_published", "created_at")
#     list_filter = ("is_published", "created_at", "category")
#     search_fields = ("translations__title", "slug")
#     ordering = ("-created_at",)
#     inlines = [ResourceDocumentInline]

#     def _title(self, obj):
#         return obj.safe_translation_getter("title", any_language=True)
#     _title.short_description = "Titre"
