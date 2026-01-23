# economic/formations/admin/enrollment_admin.py
from __future__ import annotations

from django.contrib import admin, messages
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from ..models import Enrollment

# Services optionnels (ne pas casser l'admin si non présents)
try:
    from economic.formations.services.progress_service import recompute_enrollment_progress
except Exception:
    recompute_enrollment_progress = None

try:
    # Ton projet peut avoir une fonction globale "issue certificate"
    # Exemple attendu: issue_certificate_for_enrollment(enrollment, generate_pdf=True, send_email=True)
    from economic.formations.services.certificate_service import issue_certificate_for_enrollment
except Exception:
    issue_certificate_for_enrollment = None

try:
    # Alternative si tu as uniquement ces services séparés
    from economic.formations.services.certificate_pdf import generate_certificate_pdf_and_attach
except Exception:
    generate_certificate_pdf_and_attach = None

try:
    from economic.formations.services.certificate_email import send_certificate_email
except Exception:
    send_certificate_email = None


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    # ---- List ----
    list_display = (
        "id",
        "user",
        "course",
        "session",
        "status",
        "payment_provider",
        "payment_status",
        "paid",
        "amount",
        "currency",
        "progress_percent",
        "enrolled_at",
    )
    list_filter = ("status", "payment_provider", "payment_status", "paid", "course", "session")
    search_fields = (
        "user__email",
        "user__username",
        "course__slug",
        "course__translations__title",
        "payment_reference",
    )
    ordering = ("-enrolled_at",)

    # ---- Form ----
    autocomplete_fields = ("user", "course", "session")
    readonly_fields = ("enrolled_at", "created_at", "updated_at")

    fieldsets = (
        (None, {"fields": ("user", "course", "session", "status")}),
        (_("Paiement"), {"fields": ("paid", "payment_provider", "payment_status", "amount", "currency", "payment_reference", "paid_at")}),
        (_("Progression"), {"fields": ("progress_percent", "completed", "completed_at", "last_accessed_at")}),
        (_("Audit"), {"fields": ("enrolled_at", "created_at", "updated_at")}),
    )

    actions = [
        "mark_paid_manual",
        "mark_completed",
        "mark_cancelled",
        "recompute_progress",
        "mark_completed_and_issue_certificate",
        "issue_certificate_only",
    ]

    # ------------------------------------------------------------
    # Actions (paiement)
    # ------------------------------------------------------------
    @admin.action(description=_("Marquer comme payé (manuel)"))
    def mark_paid_manual(self, request, queryset):
        ok, failed = 0, 0
        for e in queryset.select_related("course", "user"):
            try:
                e.mark_paid(provider=Enrollment.PaymentProvider.MANUAL, reference=e.payment_reference or "ADMIN", save=True)
                ok += 1
            except Exception as exc:
                failed += 1
                messages.error(request, _("Erreur paiement pour %(enr)s : %(err)s") % {"enr": str(e), "err": str(exc)})

        if ok:
            messages.success(request, _("%(n)s inscriptions marquées payées.") % {"n": ok})
        if failed:
            messages.warning(request, _("%(n)s inscriptions en échec.") % {"n": failed})

    # ------------------------------------------------------------
    # Actions (statut)
    # ------------------------------------------------------------
    @admin.action(description=_("Marquer comme terminé"))
    def mark_completed(self, request, queryset):
        ok, failed = 0, 0
        for e in queryset.select_related("course", "user"):
            try:
                e.mark_completed(save=True)
                ok += 1
            except Exception as exc:
                failed += 1
                messages.error(request, _("Erreur completion pour %(enr)s : %(err)s") % {"enr": str(e), "err": str(exc)})

        if ok:
            messages.success(request, _("%(n)s inscriptions terminées.") % {"n": ok})
        if failed:
            messages.warning(request, _("%(n)s inscriptions en échec.") % {"n": failed})

    @admin.action(description=_("Annuler inscription"))
    def mark_cancelled(self, request, queryset):
        updated = queryset.update(status=Enrollment.Status.CANCELLED)
        messages.success(request, _("%(n)s inscriptions annulées.") % {"n": updated})

    # ------------------------------------------------------------
    # Actions (progression)
    # ------------------------------------------------------------
    @admin.action(description=_("Recalculer la progression (LessonProgress → Enrollment)"))
    def recompute_progress(self, request, queryset):
        if not recompute_enrollment_progress:
            messages.error(request, _("Service progression indisponible."))
            return

        ok, failed = 0, 0
        for e in queryset.select_related("course", "user"):
            try:
                recompute_enrollment_progress(e, save=True)
                ok += 1
            except Exception as exc:
                failed += 1
                messages.error(request, _("Erreur progression pour %(enr)s : %(err)s") % {"enr": str(e), "err": str(exc)})

        if ok:
            messages.success(request, _("%(n)s progressions recalculées.") % {"n": ok})
        if failed:
            messages.warning(request, _("%(n)s inscriptions en échec.") % {"n": failed})

    # ------------------------------------------------------------
    # Actions (certificat)
    # ------------------------------------------------------------
    def _issue_certificate_fallback(self, enrollment: Enrollment, generate_pdf: bool, send_email: bool):
        """
        Fallback si tu n'as pas de service unique 'issue_certificate_for_enrollment'.
        On crée/récupère Certificate via enrollment.certificate (OneToOne) puis on appelle PDF/email si dispo.
        """
        cert = getattr(enrollment, "certificate", None)
        if cert is None:
            # import local pour éviter cycles
            from ..models import Certificate
            cert = Certificate(enrollment=enrollment)
            cert.save()

        if generate_pdf and generate_certificate_pdf_and_attach:
            generate_certificate_pdf_and_attach(cert, force=True)

        if send_email and send_certificate_email:
            send_certificate_email(cert)

        return cert

    @admin.action(description=_("Terminer + émettre certificat (PDF + email)"))
    def mark_completed_and_issue_certificate(self, request, queryset):
        ok, failed = 0, 0

        for e in queryset.select_related("course", "user"):
            try:
                with transaction.atomic():
                    e.mark_completed(save=True)

                    if issue_certificate_for_enrollment:
                        issue_certificate_for_enrollment(e, generate_pdf=True, send_email=True)
                    else:
                        self._issue_certificate_fallback(e, generate_pdf=True, send_email=True)

                ok += 1
            except Exception as exc:
                failed += 1
                messages.error(
                    request,
                    _("Erreur pour %(enr)s : %(err)s") % {"enr": str(e), "err": str(exc)}
                )

        if ok:
            messages.success(request, _("%(n)s inscriptions terminées + certificats émis.") % {"n": ok})
        if failed:
            messages.warning(request, _("%(n)s inscriptions en échec.") % {"n": failed})

    @admin.action(description=_("Émettre certificat seulement (PDF + email)"))
    def issue_certificate_only(self, request, queryset):
        ok, failed = 0, 0

        for e in queryset.select_related("course", "user"):
            try:
                with transaction.atomic():
                    if issue_certificate_for_enrollment:
                        issue_certificate_for_enrollment(e, generate_pdf=True, send_email=True)
                    else:
                        self._issue_certificate_fallback(e, generate_pdf=True, send_email=True)
                ok += 1
            except Exception as exc:
                failed += 1
                messages.error(request, _("Erreur certificat pour %(enr)s : %(err)s") % {"enr": str(e), "err": str(exc)})

        if ok:
            messages.success(request, _("%(n)s certificats émis.") % {"n": ok})
        if failed:
            messages.warning(request, _("%(n)s inscriptions en échec.") % {"n": failed})





# # economic/formations/admin/enrollment_admin.py
# from django.contrib import admin, messages
# from django.utils.translation import gettext_lazy as _
# from django.contrib.auth import get_user_model

# from ..models import Enrollment
# try:
#     from economic.formations.services.certificates import generate_certificate
# except Exception:
#     generate_certificate = None

# # --- Admin pour CustomUser, nécessaire pour autocomplete_fields ---
# CustomUser = get_user_model()

# @admin.register(CustomUser)
# class CustomUserAdmin(admin.ModelAdmin):
#     search_fields = ("email", "username")  # obligatoire pour autocomplete
#     list_display = ("email", "username", "is_active")
#     ordering = ("email",)

# # --- Admin pour Enrollment ---
# @admin.register(Enrollment)
# class EnrollmentAdmin(admin.ModelAdmin):
#     list_display = ("user", "course", "status", "completed", "enrolled_at", "completed_at")
#     list_filter = ("status", "completed", "course")
#     search_fields = (
#         "user__email",
#         "user__username",
#         "course__translations__title",
#         "course__slug",
#     )
#     ordering = ("-enrolled_at",)
#     autocomplete_fields = ("user", "course")  # fonctionne maintenant
#     readonly_fields = ("enrolled_at",)

#     actions = [
#         "mark_active",
#         "mark_cancelled",
#         "mark_completed_and_issue_certificate",
#     ]

#     @admin.action(description=_("Marquer ACTIF"))
#     def mark_active(self, request, queryset):
#         updated = queryset.update(status=Enrollment.Status.ACTIVE)
#         messages.success(request, _("%(n)s inscriptions marquées ACTIF.") % {"n": updated})

#     @admin.action(description=_("Marquer ANNULÉ"))
#     def mark_cancelled(self, request, queryset):
#         updated = queryset.update(status=Enrollment.Status.CANCELLED)
#         messages.success(request, _("%(n)s inscriptions marquées ANNULÉ.") % {"n": updated})

#     @admin.action(description=_("Marquer TERMINÉ + émettre certificat (PDF + email)"))
#     def mark_completed_and_issue_certificate(self, request, queryset):
#         ok = 0
#         failed = 0

#         for e in queryset.select_related("course", "user"):
#             try:
#                 e.mark_completed(save=True)
#                 if generate_certificate:
#                     generate_certificate(e, generate_pdf=True, send_email=True)
#                 ok += 1
#             except Exception as exc:
#                 failed += 1
#                 messages.error(
#                     request,
#                     _("Erreur pour %(enr)s : %(err)s") % {"enr": str(e), "err": str(exc)}
#                 )

#         if ok:
#             messages.success(
#                 request,
#                 _("%(n)s inscriptions terminées + certificats générés.") % {"n": ok}
#             )
#         if failed:
#             messages.warning(
#                 request,
#                 _("%(n)s inscriptions en échec.") % {"n": failed}
#             )





# from django.contrib import admin

# from ..models import Enrollment


# @admin.register(Enrollment)
# class EnrollmentAdmin(admin.ModelAdmin):
#     list_display = ("user", "course", "enrolled_at", "completed")
#     list_filter = ("completed",)
