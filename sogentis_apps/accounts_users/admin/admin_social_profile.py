# accounts_users/admin/social_profile_admin.py
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.core.mail import send_mail
from django.conf import settings

from accounts_users.models.social.social_profile import SocialProfile


@admin.register(SocialProfile)
class SocialProfileAdmin(admin.ModelAdmin):
    """
    Administration du Profil Social
    - Validation / refus d’adhésion sociale
    - Notifications email
    """

    list_display = (
        "id",
        "full_name",
        "membership_role",
        "colored_validation_status",
        "membership_date",
        "validated_at",
        "created_at",
    )

    list_filter = (
        "is_active_member",
        "is_validated",
        "membership_role",
        "created_at",
    )

    search_fields = (
        "user__email",
        "first_name",
        "last_name",
    )

    ordering = ("-created_at",)

    readonly_fields = (
        "created_at",
        "updated_at",
        "membership_date",
        "validated_at",
    )

    fieldsets = (
        (_("Profil utilisateur"), {
            "fields": (
                "user",
                "first_name", "last_name", "middle_names", "nickname",
                "date_of_birth", "place_of_birth", "country_of_birth",
                "country_of_residence", "city_of_residence", "address",
                "phone", "profession", "function",
                "profile_picture", "judicial_record",
            )
        }),
        (_("Adhésion sociale"), {
            "fields": (
                "membership_role",
                "membership_date",
                "is_active_member",
            )
        }),
        (_("Engagement"), {
            "fields": (
                "motivation",
                "availability",
                "skills",
            )
        }),
        (_("Validation"), {
            "fields": (
                "is_validated",
                "validated_at",
            )
        }),
        (_("Dates"), {"fields": ("created_at", "updated_at")}),
    )

    actions = (
        "approve_social_profiles",
        "reject_social_profiles",
    )

    # ==================================================
    # APPROVE
    # ==================================================
    @admin.action(description=_("Approuver les profils sociaux sélectionnés"))
    def approve_social_profiles(self, request, queryset):
        now = timezone.now()
        count = 0

        for social in queryset:
            if social.is_validated:
                continue

            social.is_validated = True
            social.is_active_member = True
            social.validated_at = now
            social.save(update_fields=["is_validated", "is_active_member", "validated_at"])

            # --- EMAIL ---
            send_mail(
                subject=_("Votre adhésion sociale a été approuvée"),
                message=_(
                    "Bonjour {name},\n\n"
                    "Votre adhésion sociale a été approuvée avec succès.\n"
                    "Bienvenue dans la communauté !"
                ).format(name=f"{social.first_name} {social.last_name}".strip()),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[social.user.email],
                fail_silently=True,
            )
            count += 1

        self.message_user(request, _("%(count)d profil(s) social(aux) approuvé(s).") % {"count": count})

    # ==================================================
    # REJECT
    # ==================================================
    @admin.action(description=_("Rejeter les profils sociaux sélectionnés"))
    def reject_social_profiles(self, request, queryset):
        count = 0

        for social in queryset:
            social.is_validated = False
            social.is_active_member = False
            social.validated_at = None
            social.save(update_fields=["is_validated", "is_active_member", "validated_at"])

            # --- EMAIL ---
            send_mail(
                subject=_("Votre adhésion sociale a été refusée"),
                message=_(
                    "Bonjour {name},\n\n"
                    "Votre demande d’adhésion sociale a été refusée.\n"
                    "Vous pouvez contacter l’administrateur pour plus d’informations."
                ).format(name=f"{social.first_name} {social.last_name}".strip()),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[social.user.email],
                fail_silently=True,
            )
            count += 1

        self.message_user(request, _("%(count)d profil(s) social(aux) rejeté(s).") % {"count": count})

    # ==================================================
    # STATUS BADGE
    # ==================================================
    def colored_validation_status(self, obj):
        if obj.is_validated:
            color = "success"
            label = _("Validé")
        elif obj.is_active_member:
            color = "warning"
            label = _("En attente")
        else:
            color = "danger"
            label = _("Rejeté")

        return mark_safe(f'<span class="badge bg-{color}">{label}</span>')

    colored_validation_status.short_description = _("Statut")

    # ==================================================
    # FULL NAME DISPLAY
    # ==================================================
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = _("Nom complet")






# # accounts_users/admin/social_profile_admin.py 22/12/2025
# from django.contrib import admin
# from django.utils.translation import gettext_lazy as _
# from django.utils import timezone
# from django.utils.safestring import mark_safe
# from django.core.mail import send_mail
# from django.conf import settings

# from accounts_users.models.social.social_profile import SocialProfile
# from accounts_users.models.users_profile import UserProfile


# @admin.register(SocialProfile)
# class SocialProfileAdmin(admin.ModelAdmin):
#     """
#     Administration du Profil Social
#     - Validation / refus d’adhésion sociale
#     - Synchronisation avec UserProfile
#     - Notifications email
#     """

#     list_display = (
#         "id",
#         "profile",
#         "membership_role",
#         "colored_validation_status",
#         "membership_date",
#         "validated_at",
#         "created_at",
#     )

#     list_filter = (
#         "is_active_member",
#         "is_validated",
#         "membership_role",
#         "created_at",
#     )

#     search_fields = (
#         "profile__user__email",
#         "profile__first_name",
#         "profile__last_name",
#     )

#     ordering = ("-created_at",)

#     readonly_fields = (
#         "created_at",
#         "updated_at",
#         "membership_date",
#         "validated_at",
#     )

#     fieldsets = (
#         (_("Profil utilisateur"), {"fields": ("profile",)}),
#         (
#             _("Adhésion sociale"),
#             {
#                 "fields": (
#                     "membership_role",
#                     "membership_date",
#                     "is_active_member",
#                 )
#             },
#         ),
#         (
#             _("Engagement"),
#             {
#                 "fields": (
#                     "motivation",
#                     "availability",
#                     "skills",
#                 )
#             },
#         ),
#         (
#             _("Validation"),
#             {
#                 "fields": (
#                     "is_validated",
#                     "validated_at",
#                 )
#             },
#         ),
#         (_("Dates"), {"fields": ("created_at", "updated_at")}),
#     )

#     actions = (
#         "approve_social_profiles",
#         "reject_social_profiles",
#     )

#     # ==================================================
#     # APPROVE
#     # ==================================================
#     @admin.action(description=_("Approuver les profils sociaux sélectionnés"))
#     def approve_social_profiles(self, request, queryset):
#         now = timezone.now()
#         count = 0

#         for social in queryset:
#             if social.is_validated:
#                 continue

#             # --- SocialProfile ---
#             social.is_validated = True
#             social.is_active_member = True
#             social.validated_at = now
#             social.save(
#                 update_fields=[
#                     "is_validated",
#                     "is_active_member",
#                     "validated_at",
#                 ]
#             )

#             # --- UserProfile SYNC ---
#             user_profile = social.profile
#             user_profile.status = UserProfile.Status.APPROVED

#             if not user_profile.membership_role:
#                 user_profile.membership_role = social.membership_role

#             user_profile.save(
#                 update_fields=["status", "membership_role"]
#             )

#             # --- EMAIL ---
#             send_mail(
#                 subject=_("Votre adhésion sociale a été approuvée"),
#                 message=_(
#                     "Bonjour {name},\n\n"
#                     "Votre adhésion sociale a été approuvée avec succès.\n"
#                     "Bienvenue dans la communauté !"
#                 ).format(
#                     name=f"{user_profile.first_name} {user_profile.last_name}".strip()
#                 ),
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 recipient_list=[user_profile.user.email],
#                 fail_silently=True,
#             )

#             count += 1

#         self.message_user(
#             request,
#             _("%(count)d profil(s) social(aux) approuvé(s).") % {"count": count},
#         )

#     # ==================================================
#     # REJECT
#     # ==================================================
#     @admin.action(description=_("Rejeter les profils sociaux sélectionnés"))
#     def reject_social_profiles(self, request, queryset):
#         count = 0

#         for social in queryset:
#             # --- SocialProfile ---
#             social.is_validated = False
#             social.is_active_member = False
#             social.validated_at = None
#             social.save(
#                 update_fields=[
#                     "is_validated",
#                     "is_active_member",
#                     "validated_at",
#                 ]
#             )

#             # --- UserProfile SYNC ---
#             user_profile = social.profile
#             user_profile.status = UserProfile.Status.REJECTED
#             user_profile.save(update_fields=["status"])

#             # --- EMAIL ---
#             send_mail(
#                 subject=_("Votre adhésion sociale a été refusée"),
#                 message=_(
#                     "Bonjour {name},\n\n"
#                     "Votre demande d’adhésion sociale a été refusée.\n"
#                     "Vous pouvez contacter l’administrateur pour plus d’informations."
#                 ).format(
#                     name=f"{user_profile.first_name} {user_profile.last_name}".strip()
#                 ),
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 recipient_list=[user_profile.user.email],
#                 fail_silently=True,
#             )

#             count += 1

#         self.message_user(
#             request,
#             _("%(count)d profil(s) social(aux) rejeté(s).") % {"count": count},
#         )

#     # ==================================================
#     # STATUS BADGE
#     # ==================================================
#     def colored_validation_status(self, obj):
#         if obj.is_validated:
#             color = "success"
#             label = _("Validé")
#         elif obj.is_active_member:
#             color = "warning"
#             label = _("En attente")
#         else:
#             color = "danger"
#             label = _("Rejeté")

#         return mark_safe(
#             f'<span class="badge bg-{color}">{label}</span>'
#         )

#     colored_validation_status.short_description = _("Statut")





# # accounts_users/admin/social_profile_admin.py
# from django.contrib import admin
# from django.utils.translation import gettext_lazy as _
# from django.utils import timezone
# from django.utils.safestring import mark_safe

# from accounts_users.models.social.social_profile import SocialProfile


# @admin.register(SocialProfile)
# class SocialProfileAdmin(admin.ModelAdmin):
#     """
#     Administration du Profil Social
#     - Validation / refus d’adhésion sociale
#     - Vue claire pour les administrateurs
#     """

#     # ==================================================
#     # LISTE
#     # ==================================================
#     list_display = (
#         "id",
#         "profile",
#         "membership_role",
#         "colored_validation_status",
#         "membership_date",
#         "validated_at",
#         "created_at",
#     )

#     list_filter = (
#         "is_active_member",
#         "is_validated",
#         "membership_role",
#         "created_at",
#     )

#     search_fields = (
#         "profile__user__email",
#         "profile__first_name",
#         "profile__last_name",
#     )

#     ordering = ("-created_at",)

#     # ==================================================
#     # LECTURE SEULE
#     # ==================================================
#     readonly_fields = (
#         "created_at",
#         "updated_at",
#         "membership_date",
#         "validated_at",
#     )

#     # ==================================================
#     # GROUPES DE CHAMPS
#     # ==================================================
#     fieldsets = (
#         (
#             _("Profil utilisateur"),
#             {
#                 "fields": ("profile",)
#             },
#         ),
#         (
#             _("Adhésion sociale"),
#             {
#                 "fields": (
#                     "membership_role",
#                     "membership_date",
#                     "is_active_member",
#                 )
#             },
#         ),
#         (
#             _("Engagement"),
#             {
#                 "fields": (
#                     "motivation",
#                     "availability",
#                     "skills",
#                 )
#             },
#         ),
#         (
#             _("Validation"),
#             {
#                 "fields": (
#                     "is_validated",
#                     "validated_at",
#                 )
#             },
#         ),
#         (
#             _("Dates"),
#             {
#                 "fields": (
#                     "created_at",
#                     "updated_at",
#                 )
#             },
#         ),
#     )

#     # ==================================================
#     # ACTIONS ADMIN
#     # ==================================================
#     actions = (
#         "approve_social_profiles",
#         "reject_social_profiles",
#     )

#     # ==================================================
#     # ACTION : APPROUVER
#     # ==================================================
#     @admin.action(description=_("Approuver les profils sociaux sélectionnés"))
#     def approve_social_profiles(self, request, queryset):
#         now = timezone.now()
#         count = 0

#         for profile in queryset:
#             if not profile.is_validated:
#                 profile.is_validated = True
#                 profile.is_active_member = True
#                 profile.validated_at = now
#                 profile.save(
#                     update_fields=[
#                         "is_validated",
#                         "is_active_member",
#                         "validated_at",
#                     ]
#                 )
#                 count += 1

#         self.message_user(
#             request,
#             _("%(count)d profil(s) social(aux) approuvé(s).") % {"count": count},
#         )

#     # ==================================================
#     # ACTION : REJETER
#     # ==================================================
#     @admin.action(description=_("Rejeter les profils sociaux sélectionnés"))
#     def reject_social_profiles(self, request, queryset):
#         count = 0

#         for profile in queryset:
#             profile.is_validated = False
#             profile.is_active_member = False
#             profile.validated_at = None
#             profile.save(
#                 update_fields=[
#                     "is_validated",
#                     "is_active_member",
#                     "validated_at",
#                 ]
#             )
#             count += 1

#         self.message_user(
#             request,
#             _("%(count)d profil(s) social(aux) rejeté(s).") % {"count": count},
#         )

#     # ==================================================
#     # AFFICHAGE PERSONNALISÉ
#     # ==================================================
#     def colored_validation_status(self, obj):
#         if obj.is_validated:
#             color = "success"
#             label = _("Validé")
#         elif obj.is_active_member:
#             color = "warning"
#             label = _("En attente")
#         else:
#             color = "danger"
#             label = _("Rejeté")

#         return mark_safe(
#             f'<span class="badge bg-{color}">{label}</span>'
#         )

#     colored_validation_status.short_description = _("Statut")
