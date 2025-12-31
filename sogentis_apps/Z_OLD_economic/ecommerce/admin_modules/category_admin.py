# economic/ecommerce/admin_modules/category_admin.py

from django.contrib import admin
from parler.admin import TranslatableAdmin
from economic.ecommerce.models import Category


@admin.register(Category)
class CategoryAdmin(TranslatableAdmin):

    list_display = ("translated_name", "slug", "order", "icon")
    list_filter = ("order",)
    search_fields = ("translations__name",)

    # ❌ IMPORTANT : ne JAMAIS utiliser prepopulated_fields avec Parler
    # prepopulated_fields = {"slug": ("name",)}

    ordering = ("order", "slug")  # 'name' interdit : champ traduit

    fieldsets = (
        ("Informations", {
            "fields": ("name", "slug", "description")
        }),
        ("Affichage", {
            "fields": ("icon", "order")
        }),
    )

    # ---- Méthodes utilitaires ----

    def translated_name(self, obj):
        return obj.safe_translation_getter("name", any_language=True)
    translated_name.short_description = "Nom"







# # /ecommerce/admin_modules/category_admin.py

# from django.contrib import admin
# from parler.admin import TranslatableAdmin
# from economic.ecommerce.models import Category


# @admin.register(Category)
# class CategoryAdmin(TranslatableAdmin):
#     list_display = ("name", "slug", "is_active", "created_at")
#     list_filter = ("is_active",)
#     search_fields = ("translations__name", "slug")
#     prepopulated_fields = {"slug": ("name",)}
#     ordering = ("name",)

#     fieldsets = (
#         (None, {
#             "fields": ("name", "slug", "is_active")
#         }),
#     )






# from django.contrib import admin
# from parler.admin import TranslatableAdmin
# from economic.ecommerce.models import Category

# @admin.register(Category)
# class CategoryAdmin(TranslatableAdmin):
#     list_display = ("name", "slug")
#     search_fields = ("name",)
#     ordering = ("slug",)  # must be real DB field
