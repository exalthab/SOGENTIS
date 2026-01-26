# economic/ecommerce/admin/sku_sequence_admin.py
from __future__ import annotations

from django.contrib import admin, messages
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from economic.ecommerce.models import SkuSequence


# ------------------------------------------------------------
# Actions (prod)
# ------------------------------------------------------------
@admin.action(description=_("Normaliser les codes (MAJ + trim)"))
def action_normalize_codes(modeladmin, request, queryset):
    updated = 0
    for seq in queryset.only("id", "vendor_code", "category_code"):
        v = (seq.vendor_code or "").strip().upper()
        c = (seq.category_code or "").strip().upper()
        if v != seq.vendor_code or c != seq.category_code:
            SkuSequence.objects.filter(pk=seq.pk).update(
                vendor_code=v,
                category_code=c,
                updated_at=models.functions.Now(),
            )
            updated += 1

    modeladmin.message_user(
        request,
        _("%(n)s séquence(s) normalisée(s).") % {"n": updated},
        level=messages.SUCCESS,
    )


@admin.action(description=_("Réinitialiser last_number à 0 (sélection)"))
def action_reset_last_number(modeladmin, request, queryset):
    n = queryset.update(last_number=0, updated_at=models.functions.Now())
    modeladmin.message_user(
        request,
        _("%(n)s séquence(s) réinitialisée(s).") % {"n": n},
        level=messages.WARNING,
    )


@admin.action(description=_("Incrémenter last_number (+1) (sélection)"))
def action_bump_last_number(modeladmin, request, queryset):
    n = queryset.update(last_number=models.F("last_number") + 1, updated_at=models.functions.Now())
    modeladmin.message_user(
        request,
        _("%(n)s séquence(s) incrémentée(s).") % {"n": n},
        level=messages.SUCCESS,
    )


@admin.action(description=_("Dédupliquer (fusionner) les doublons après normalisation"))
def action_merge_duplicates(modeladmin, request, queryset):
    """
    Prod-safe: on normalise d'abord les codes, puis on fusionne les doublons
    (même vendor_code/category_code) en gardant le last_number max.
    """
    # 1) normalise sur le queryset (sans message)
    ids = list(queryset.values_list("id", flat=True))
    for seq in SkuSequence.objects.filter(id__in=ids).only("id", "vendor_code", "category_code"):
        v = (seq.vendor_code or "").strip().upper()
        c = (seq.category_code or "").strip().upper()
        if v != seq.vendor_code or c != seq.category_code:
            SkuSequence.objects.filter(pk=seq.pk).update(
                vendor_code=v,
                category_code=c,
                updated_at=models.functions.Now(),
            )

    # 2) fusion
    merged = 0
    with transaction.atomic():
        # On regroupe sur toutes les lignes concernées
        rows = list(
            SkuSequence.objects.select_for_update()
            .filter(id__in=ids)
            .values("vendor_code", "category_code")
            .annotate(cnt=models.Count("id"), max_last=models.Max("last_number"), min_id=models.Min("id"))
            .filter(cnt__gt=1)
        )

        for g in rows:
            v = g["vendor_code"]
            c = g["category_code"]
            keep_id = g["min_id"]
            max_last = int(g["max_last"] or 0)

            # update keep with max last_number
            SkuSequence.objects.filter(pk=keep_id).update(
                last_number=max_last,
                updated_at=models.functions.Now(),
            )

            # delete others
            SkuSequence.objects.filter(vendor_code=v, category_code=c).exclude(pk=keep_id).delete()
            merged += 1

    modeladmin.message_user(
        request,
        _("Fusion effectuée pour %(n)s groupe(s) de doublons.") % {"n": merged},
        level=messages.SUCCESS,
    )


# ------------------------------------------------------------
# Admin (production)
# ------------------------------------------------------------
@admin.register(SkuSequence)
class SkuSequenceAdmin(admin.ModelAdmin):
    save_on_top = True
    actions_on_top = True
    actions_on_bottom = True
    list_per_page = 50

    list_display = ("id", "vendor_code", "category_code", "last_number", "created_at", "updated_at")
    list_display_links = ("id", "vendor_code", "category_code")

    ordering = ("vendor_code", "category_code", "id")

    list_filter = (
        ("created_at", admin.DateFieldListFilter),
        ("updated_at", admin.DateFieldListFilter),
    )

    search_fields = ("vendor_code", "category_code")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (_("Clés"), {"fields": ("vendor_code", "category_code")}),
        (_("Séquence"), {"fields": ("last_number",)}),
        (_("Système"), {"fields": ("created_at", "updated_at")}),
    )

    actions = (
        action_normalize_codes,
        action_merge_duplicates,
        action_bump_last_number,
        action_reset_last_number,
    )

    def save_model(self, request, obj: SkuSequence, form, change):
        # normalisation prod
        obj.vendor_code = (obj.vendor_code or "").strip().upper()
        obj.category_code = (obj.category_code or "").strip().upper()
        super().save_model(request, obj, form, change)
