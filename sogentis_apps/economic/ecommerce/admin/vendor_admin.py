from __future__ import annotations

from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _

from economic.ecommerce.models import Vendor


class VendorCodeFilter(admin.SimpleListFilter):
    title = _("Code vendeur (VENDORCODE)")
    parameter_name = "code_presence"

    def lookups(self, request, model_admin):
        return (
            ("with", _("Avec code")),
            ("without", _("Sans code")),
        )

    def queryset(self, request, queryset):
        v = self.value()
        if v == "with":
            return queryset.exclude(code__isnull=True).exclude(code__exact="")
        if v == "without":
            return queryset.filter(code__isnull=True) | queryset.filter(code__exact="")
        return queryset


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    # -------------------------
    # UX / perf
    # -------------------------
    save_on_top = True
    actions_on_top = True
    actions_on_bottom = True
    list_per_page = 50
    date_hierarchy = "created_at"
    autocomplete_fields = ("user",)

    # -------------------------
    # List
    # -------------------------
    list_display = (
        "id",
        "code",
        "company_name",
        "user_email",
        "is_active",
        "is_verified",
        "verified_at",
        "updated_at",
    )
    list_display_links = ("id", "company_name")
    list_editable = ("is_active", "is_verified")
    ordering = ("-is_verified", "-is_active", "company_name", "id")

    list_filter = (
        "is_active",
        "is_verified",
        VendorCodeFilter,
        ("created_at", admin.DateFieldListFilter),
        ("verified_at", admin.DateFieldListFilter),
    )

    search_fields = (
        "company_name",
        "code",
        "slug",
        "contact_email",
        "phone",
        "user__email",
        "user__phone",
        "user__first_name",
        "user__last_name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "verified_at",
    )

    # Optimisation requêtes
    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")

    @admin.display(description=_("Email utilisateur"), ordering="user__email")
    def user_email(self, obj: Vendor) -> str:
        return getattr(obj.user, "email", "") or "—"

    # -------------------------
    # Form layout
    # -------------------------
    fieldsets = (
        (_("Identité"), {"fields": ("user", "company_name", "slug", "code")}),
        (_("Contacts"), {"fields": ("contact_email", "phone", "address")}),
        (_("Statut marketplace"), {"fields": ("is_active", "is_verified", "verified_at")}),
        (_("Système"), {"fields": ("created_at", "updated_at")}),
    )

    # -------------------------
    # Actions pro (respect modèle)
    # -------------------------
    actions = (
        "action_verify",
        "action_unverify",
        "action_activate",
        "action_deactivate",
        "action_normalize_codes",
    )

    @admin.action(description=_("Vérifier (met à jour verified_at, applique validations)"))
    def action_verify(self, request, queryset):
        updated = 0
        skipped = 0

        # Important: on passe par save() pour respecter clean/save
        for v in queryset.select_related("user"):
            if not v.is_active:
                skipped += 1
                continue
            if v.is_verified:
                continue
            v.is_verified = True
            try:
                v.save()
                updated += 1
            except Exception:
                skipped += 1

        if updated:
            self.message_user(
                request,
                _("%(n)s vendeur(s) vérifié(s).") % {"n": updated},
                level=messages.SUCCESS,
            )
        if skipped:
            self.message_user(
                request,
                _("%(n)s vendeur(s) ignoré(s) (inactif(s) ou erreur validation).") % {"n": skipped},
                level=messages.WARNING,
            )

    @admin.action(description=_("Retirer la vérification (vide verified_at, applique validations)"))
    def action_unverify(self, request, queryset):
        updated = 0
        skipped = 0

        for v in queryset.select_related("user"):
            if not v.is_verified:
                continue
            v.is_verified = False
            try:
                v.save()
                updated += 1
            except Exception:
                skipped += 1

        if updated:
            self.message_user(
                request,
                _("%(n)s vendeur(s) dé-vérifié(s).") % {"n": updated},
                level=messages.SUCCESS,
            )
        if skipped:
            self.message_user(
                request,
                _("%(n)s vendeur(s) ignoré(s) (erreur validation).") % {"n": skipped},
                level=messages.WARNING,
            )

    @admin.action(description=_("Activer les vendeurs sélectionnés"))
    def action_activate(self, request, queryset):
        # Activation simple (le modèle tolère)
        n = queryset.update(is_active=True)
        self.message_user(request, _("%(n)s vendeur(s) activé(s).") % {"n": n}, messages.SUCCESS)

    @admin.action(description=_("Désactiver les vendeurs (dé-vérifie si nécessaire)"))
    def action_deactivate(self, request, queryset):
        updated = 0
        for v in queryset:
            # règle métier: inactif ne peut pas rester vérifié
            v.is_active = False
            v.is_verified = False
            try:
                v.save()
                updated += 1
            except Exception:
                pass
        self.message_user(
            request,
            _("%(n)s vendeur(s) désactivé(s).") % {"n": updated},
            level=messages.SUCCESS,
        )

    @admin.action(description=_("Normaliser les codes (trim + UPPER, vide => NULL)"))
    def action_normalize_codes(self, request, queryset):
        changed = 0
        objs = list(queryset.only("id", "code"))
        for obj in objs:
            before = obj.code
            after = (before or "").strip().upper() or None
            if before != after:
                obj.code = after
                changed += 1
        if changed:
            Vendor.objects.bulk_update(objs, ["code"])
        self.message_user(
            request,
            _("%(n)s vendeur(s) mis à jour (code normalisé).") % {"n": changed},
            level=messages.SUCCESS,
        )





# # economic/ecommerce/admin/vendor_admin.py
# from __future__ import annotations

# from django.contrib import admin
# from django.utils.translation import gettext_lazy as _

# from economic.ecommerce.models import Vendor


# @admin.action(description=_("Vérifier les vendeurs sélectionnés"))
# def verify_vendors(modeladmin, request, queryset):
#     queryset.update(is_verified=True)


# @admin.action(description=_("Retirer la vérification"))
# def unverify_vendors(modeladmin, request, queryset):
#     queryset.update(is_verified=False)


# @admin.register(Vendor)
# class VendorAdmin(admin.ModelAdmin):
#     list_display = ("id", "company_name", "user", "is_verified", "created_at")
#     list_filter = ("is_verified", "created_at")
#     search_fields = ("company_name", "user__email", "user__phone", "user__first_name", "user__last_name")
#     ordering = ("-created_at",)
#     readonly_fields = ("created_at",)
#     autocomplete_fields = ("user",)

#     actions = [verify_vendors, unverify_vendors]

#     fieldsets = (
#         (_("Identité"), {"fields": ("user", "company_name")}),
#         (_("Statut"), {"fields": ("is_verified",)}),
#         (_("Dates"), {"fields": ("created_at",)}),
#     )





# # /economic/ecommerce/admin/vendor_admin.py

# from django.contrib import admin
# from django.utils.translation import gettext_lazy as _

# from economic.ecommerce.models import Vendor


# @admin.action(description=_("Vérifier les vendeurs sélectionnés"))
# def verify_vendors(modeladmin, request, queryset):
#     queryset.update(is_verified=True)


# @admin.action(description=_("Retirer la vérification"))
# def unverify_vendors(modeladmin, request, queryset):
#     queryset.update(is_verified=False)


# @admin.register(Vendor)
# class VendorAdmin(admin.ModelAdmin):
#     list_display = ("id", "company_name", "user", "is_verified", "created_at")
#     list_filter = ("is_verified", "created_at")
#     search_fields = ("company_name", "user__email", "user__username")
#     ordering = ("-created_at",)
#     readonly_fields = ("created_at",)

#     actions = [verify_vendors, unverify_vendors]

#     fieldsets = (
#         (_("Identité"), {"fields": ("user", "company_name")}),
#         (_("Statut"), {"fields": ("is_verified",)}),
#         (_("Dates"), {"fields": ("created_at",)}),
#     )
