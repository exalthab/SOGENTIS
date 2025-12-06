#about/models.py
from .models.about_page import AboutPage
from .models.about_section import AboutSection
from .models.objective_item import ObjectiveItem
from .models.team_member import TeamMember
from .models.partner import Partner
from .models.child import Child
from .models.mother import Mother
from .models.sponsor import Sponsor





# #about/models.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from parler.models import TranslatableModel, TranslatedFields
# from datetime import date


# # =============================
# # 🌐 PAGE PRINCIPALE "À propos"
# # =============================
# class AboutPage(TranslatableModel):
#     translations = TranslatedFields(
#         title=models.CharField(_("Titre"), max_length=200),
#         subtitle=models.CharField(_("Sous-titre"), max_length=255, blank=True, null=True),
#         content=models.TextField(_("Contenu")),
#         mission=models.TextField(_("Mission"), blank=True, null=True),
#         vision=models.TextField(_("Vision"), blank=True, null=True),
#     )
#     created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
#     updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

#     class Meta:
#         verbose_name = _("À propos de SOGENTIS")
#         verbose_name_plural = _("À propos de SOGENTIS")

#     def __str__(self):
#         return self.safe_translation_getter("title", any_language=True)


# # =============================
# # 🧩 SECTIONS DYNAMIQUES
# # =============================
# class AboutSection(TranslatableModel):
#     SECTION_CHOICES = [
#         ('about', _("À propos de SOGENTIS")),
#         ('history', _("Historique")),
#         ('mission', _("Mission")),
#         ('vision', _("Vision")),
#         ('objectives', _("Objectifs")),
#         ('values', _("Nos valeurs")),
#         ('team', _("Notre équipe")),
#         ('children', _("Enfants")),
#         ('mothers', _("Mamans")),
#         ('partners', _("Partenaires")),
#     ]

#     translations = TranslatedFields(
#         title=models.CharField(_("Titre"), max_length=200),
#         subtitle=models.CharField(_("Sous-titre"), max_length=255, blank=True, null=True),
#         content=models.TextField(_("Contenu")),
#     )
#     section_type = models.CharField(_("Type de section"), max_length=30, choices=SECTION_CHOICES)
#     image = models.ImageField(_("Image"), upload_to="about/images/", blank=True, null=True)
#     order = models.PositiveIntegerField(_("Ordre d’affichage"), default=0)
#     is_active = models.BooleanField(_("Actif"), default=True)
#     created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
#     updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

#     class Meta:
#         verbose_name = _("Section À propos")
#         verbose_name_plural = _("Sections À propos")
#         ordering = ['order']

#     def __str__(self):
#         return f"{self.get_section_type_display()} - {self.safe_translation_getter('title', any_language=True)}"

#     def image_url(self):
#         return self.image.url if self.image else "/static/about/img/default_section.png"


# # =============================
# # 👥 ÉQUIPE
# # =============================
# class TeamMember(TranslatableModel):
#     translations = TranslatedFields(
#         name=models.CharField(_("Nom"), max_length=100),
#         role=models.CharField(_("Rôle"), max_length=100),
#         bio=models.TextField(_("Biographie"), blank=True, null=True),
#     )
#     photo = models.ImageField(_("Photo"), upload_to="about/images/team/", blank=True, null=True)
#     order = models.PositiveIntegerField(_("Ordre"), default=0)
#     is_active = models.BooleanField(_("Actif"), default=True)
#     created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
#     updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

#     class Meta:
#         verbose_name = _("Membre de l'équipe")
#         verbose_name_plural = _("Membres de l'équipe")
#         ordering = ['order']

#     def __str__(self):
#         return f"{self.safe_translation_getter('name', any_language=True)}"

#     def photo_url(self):
#         return self.photo.url if self.photo else "/static/about/img/default_team.png"


# # =============================
# # 🤝 PARTENAIRES
# # =============================
# class Partner(TranslatableModel):
#     translations = TranslatedFields(
#         name=models.CharField(_("Nom du partenaire"), max_length=100),
#         description=models.TextField(_("Description"), blank=True, null=True),
#     )
#     logo = models.ImageField(_("Logo"), upload_to="about/images/partners/", blank=True, null=True)
#     website = models.URLField(_("Site web"), blank=True, null=True)
#     order = models.PositiveIntegerField(_("Ordre"), default=0)
#     is_active = models.BooleanField(_("Actif"), default=True)
#     created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
#     updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

#     class Meta:
#         verbose_name = _("Partenaire")
#         verbose_name_plural = _("Partenaires")
#         ordering = ['order']

#     def __str__(self):
#         return self.safe_translation_getter("name", any_language=True)

#     def logo_url(self):
#         return self.logo.url if self.logo else "/static/about/img/default_partner.png"


# # =============================
# # 👶 ENFANTS
# # =============================
# class Child(TranslatableModel):
#     GENDER_CHOICES = (
#         ('M', _('Garçon')),
#         ('F', _('Fille')),
#     )

#     name = models.CharField(_("Nom complet"), max_length=200)
#     gender = models.CharField(_("Sexe"), max_length=1, choices=GENDER_CHOICES, default='M')
#     photo = models.ImageField(_("Photo"), upload_to="about/images/children/", blank=True, null=True)
#     registration_number = models.CharField(_("N° d’enregistrement"), max_length=50, unique=True)
#     date_of_birth = models.DateField(_("Date de naissance"), null=True, blank=True)
#     school = models.CharField(_("École fréquentée"), max_length=255, blank=True)
#     short_story = models.TextField(_("Petite histoire / description"), blank=True)
#     is_active = models.BooleanField(_("Actif"), default=True)
#     created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
#     updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

#     class Meta:
#         verbose_name = _("Enfant")
#         verbose_name_plural = _("Enfants")
#         ordering = ["name"]

#     def __str__(self):
#         return self.name

#     @property
#     def age(self):
#         if self.date_of_birth:
#             today = date.today()
#             return today.year - self.date_of_birth.year - (
#                 (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
#             )
#         return None

#     def photo_url(self):
#         if self.photo:
#             return self.photo.url
#         return "/static/about/img/default_female.png" if self.gender == "F" else "/static/about/img/default_male.png"


# # =============================
# # 🤱 MAMANS
# # =============================
# class Mother(TranslatableModel):
#     translations = TranslatedFields(
#         name=models.CharField(_("Nom complet"), max_length=100),
#         story=models.TextField(_("Histoire / description"), blank=True),
#     )
#     registration_number = models.CharField(_("N° d’enregistrement"), max_length=50, unique=True)
#     photo = models.ImageField(_("Photo"), upload_to='about/images/mothers/', blank=True, null=True)
#     is_active = models.BooleanField(_("Actif"), default=True)
#     created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
#     updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

#     class Meta:
#         verbose_name = _("Maman")
#         verbose_name_plural = _("Mamans")
#         ordering = ['registration_number']

#     def __str__(self):
#         return self.safe_translation_getter("name", any_language=True)

#     def photo_url(self):
#         return self.photo.url if self.photo else "/static/about/img/default_female.png"


# # =============================
# # 🎯 OBJECTIFS
# # =============================
# class Objective(TranslatableModel):
#     translations = TranslatedFields(
#         title=models.CharField(_("Titre"), max_length=200),
#         description=models.TextField(_("Description")),
#     )
#     icon = models.CharField(_("Icône (classe CSS)"), max_length=100, blank=True, null=True)
#     order = models.PositiveIntegerField(_("Ordre"), default=0)
#     is_active = models.BooleanField(_("Actif"), default=True)
#     created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
#     updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

#     class Meta:
#         verbose_name = _("Objectif")
#         verbose_name_plural = _("Objectifs")
#         ordering = ['order']

#     def __str__(self):
#         return self.safe_translation_getter("title", any_language=True)

# # =============================
# # 💝 SPONSORS
# # =============================
# class Sponsor(TranslatableModel):
#     name = models.CharField(_("Nom du sponsor"), max_length=255)
#     email = models.EmailField(_("Email"), unique=True)

#     class Meta:
#         verbose_name = _("Sponsor")
#         verbose_name_plural = _("Sponsors")
#         ordering = ["name"]

#     def __str__(self):
#         return self.name


# # =============================
# # 💸 DONS POUR ENFANTS
# # =============================
# class ChildDonation(TranslatableModel):
#     child = models.ForeignKey(
#         'Child',
#         verbose_name=_("Enfant"),
#         on_delete=models.CASCADE,
#         related_name="donations"
#     )
#     sponsor = models.ForeignKey(
#         'Sponsor',
#         verbose_name=_("Sponsor"),
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name="donations"
#     )
#     amount = models.DecimalField(_("Montant"), max_digits=10, decimal_places=2, default=0)
#     date = models.DateField(_("Date du don"), auto_now_add=True)

#     class Meta:
#         verbose_name = _("Don pour enfant")
#         verbose_name_plural = _("Dons pour enfants")
#         ordering = ["-date"]

#     def __str__(self):
#         sponsor_name = self.sponsor.name if self.sponsor else _("Anonyme")
#         return f"{sponsor_name} → {self.child.name} ({self.amount} FCFA)"




# #about/models.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from datetime import date

# # =============================
# # 🌐 PAGE PRINCIPALE "À propos"
# # =============================
# class AboutPage(models.Model):
#     title = models.CharField(_("Titre"), max_length=200)
#     subtitle = models.CharField(_("Sous-titre"), max_length=255, blank=True, null=True)
#     content = models.TextField(_("Contenu"))
#     mission = models.TextField(_("Mission"), blank=True, null=True)
#     vision = models.TextField(_("Vision"), blank=True, null=True)
#     created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
#     updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

#     class Meta:
#         verbose_name = _("À propos de SOGENTIS")
#         verbose_name_plural = _("À propos de SOGENTIS")

#     def __str__(self):
#         return self.title


# # =============================
# # 🧩 SECTIONS DYNAMIQUES
# # =============================
# class AboutSection(models.Model):
#     SECTION_CHOICES = [
#         ('about', _("À propos de SOGENTIS")),
#         ('history', _("Historique")),
#         ('mission', _("Mission")),
#         ('vision', _("Vision")),
#         ('objectives', _("Objectifs")),
#         ('values', _("Nos valeurs")),
#         ('team', _("Notre équipe")),
#         ('children', _("Enfants")),
#         ('mothers', _("Mamans")),
#         ('partners', _("Partenaires")),
#     ]

#     title = models.CharField(_("Titre"), max_length=200)
#     subtitle = models.CharField(_("Sous-titre"), max_length=255, blank=True, null=True)
#     content = models.TextField(_("Contenu"))
#     section_type = models.CharField(_("Type de section"), max_length=30, choices=SECTION_CHOICES)
#     image = models.ImageField(_("Image"), upload_to="about/images/", blank=True, null=True)
#     order = models.PositiveIntegerField(_("Ordre d’affichage"), default=0)
#     is_active = models.BooleanField(_("Actif"), default=True)
#     created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
#     updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

#     class Meta:
#         verbose_name = _("Section À propos")
#         verbose_name_plural = _("Sections À propos")
#         ordering = ['order']

#     def __str__(self):
#         return f"{self.get_section_type_display()} - {self.title}"

#     def image_url(self):
#         return self.image.url if self.image else "/static/about/img/default_section.png"


# # =============================
# # 👥 ÉQUIPE
# # =============================
# class TeamMember(models.Model):
#     name = models.CharField(_("Nom"), max_length=100)
#     role = models.CharField(_("Rôle"), max_length=100)
#     bio = models.TextField(_("Biographie"), blank=True, null=True)
#     photo = models.ImageField(_("Photo"), upload_to="about/images/team/", blank=True, null=True)
#     order = models.PositiveIntegerField(_("Ordre"), default=0)
#     is_active = models.BooleanField(_("Actif"), default=True)
#     created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
#     updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

#     class Meta:
#         verbose_name = _("Membre de l'équipe")
#         verbose_name_plural = _("Membres de l'équipe")
#         ordering = ['order']

#     def __str__(self):
#         return f"{self.name} ({self.role})"

#     def photo_url(self):
#         return self.photo.url if self.photo else "/static/about/img/default_team.png"


# # =============================
# # 🤝 PARTENAIRES
# # =============================
# class Partner(models.Model):
#     name = models.CharField(_("Nom du partenaire"), max_length=100)
#     logo = models.ImageField(_("Logo"), upload_to="about/images/partners/", blank=True, null=True)
#     website = models.URLField(_("Site web"), blank=True, null=True)
#     description = models.TextField(_("Description"), blank=True, null=True)
#     order = models.PositiveIntegerField(_("Ordre"), default=0)
#     is_active = models.BooleanField(_("Actif"), default=True)
#     created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
#     updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

#     class Meta:
#         verbose_name = _("Partenaire")
#         verbose_name_plural = _("Partenaires")
#         ordering = ['order']

#     def __str__(self):
#         return self.name

#     def logo_url(self):
#         return self.logo.url if self.logo else "/static/about/img/default_partner.png"


# # =============================
# # 👶 ENFANTS
# # =============================
# class Child(models.Model):
#     GENDER_CHOICES = (
#         ('M', _('Garçon')),
#         ('F', _('Fille')),
#     )

#     name = models.CharField(_("Nom complet"), max_length=200)
#     gender = models.CharField(_("Sexe"), max_length=1, choices=GENDER_CHOICES, default='M')
#     photo = models.ImageField(_("Photo"), upload_to="about/images/children/", blank=True, null=True)
#     registration_number = models.CharField(_("N° d’enregistrement"), max_length=50, unique=True)
#     date_of_birth = models.DateField(_("Date de naissance"), null=True, blank=True)
#     school = models.CharField(_("École fréquentée"), max_length=255, blank=True)
#     short_story = models.TextField(_("Petite histoire / description"), blank=True)
#     is_active = models.BooleanField(_("Actif"), default=True)
#     created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
#     updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

#     class Meta:
#         verbose_name = _("Enfant")
#         verbose_name_plural = _("Enfants")
#         ordering = ["name"]

#     def __str__(self):
#         return self.name

#     @property
#     def age(self):
#         if self.date_of_birth:
#             today = date.today()
#             return today.year - self.date_of_birth.year - (
#                 (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
#             )
#         return None

#     def photo_url(self):
#         if self.photo:
#             return self.photo.url
#         return "/static/about/img/default_female.png" if self.gender == "F" else "/static/about/img/default_male.png"


# # =============================
# # 🎗️ SPONSORS & DONS ENFANTS
# # =============================
# class Sponsor(models.Model):
#     name = models.CharField(_("Nom"), max_length=100)
#     email = models.EmailField(_("Email"), blank=True, null=True)

#     class Meta:
#         verbose_name = _("Parrain / Sponsor")
#         verbose_name_plural = _("Parrains / Sponsors")

#     def __str__(self):
#         return self.name or _("Anonyme")


# class ChildDonation(models.Model):
#     child = models.ForeignKey(
#         Child,
#         on_delete=models.CASCADE,
#         related_name="donations",
#         verbose_name=_("Enfant"),
#     )
#     sponsor = models.ForeignKey(
#         Sponsor,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         verbose_name=_("Sponsor"),
#     )
#     amount = models.DecimalField(_("Montant (FCFA)"), max_digits=10, decimal_places=2)
#     date = models.DateField(_("Date du don"), auto_now_add=True)

#     class Meta:
#         verbose_name = _("Don")
#         verbose_name_plural = _("Dons")
#         ordering = ["-date"]

#     def __str__(self):
#         sponsor_name = self.sponsor.name if self.sponsor else _("Anonyme")
#         return f"{sponsor_name} → {self.child.name} ({self.amount} FCFA)"


# # =============================
# # 🤱 MAMANS
# # =============================
# class Mother(models.Model):
#     name = models.CharField(_("Nom complet"), max_length=100)
#     registration_number = models.CharField(_("N° d’enregistrement"), max_length=50, unique=True)
#     story = models.TextField(_("Histoire / description"), blank=True)
#     photo = models.ImageField(_("Photo"), upload_to='about/images/mothers/', blank=True, null=True)
#     is_active = models.BooleanField(_("Actif"), default=True)
#     created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
#     updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

#     class Meta:
#         verbose_name = _("Maman")
#         verbose_name_plural = _("Mamans")
#         ordering = ['name']

#     def __str__(self):
#         return self.name

#     def photo_url(self):
#         return self.photo.url if self.photo else "/static/about/img/default_female.png"


# # =============================
# # 🎯 OBJECTIFS
# # =============================
# class Objective(models.Model):
#     title = models.CharField(_("Titre"), max_length=200)
#     description = models.TextField(_("Description"))
#     icon = models.CharField(_("Icône (classe CSS)"), max_length=100, blank=True, null=True)
#     order = models.PositiveIntegerField(_("Ordre"), default=0)
#     is_active = models.BooleanField(_("Actif"), default=True)
#     created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
#     updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

#     class Meta:
#         verbose_name = _("Objectif")
#         verbose_name_plural = _("Objectifs")
#         ordering = ['order']

#     def __str__(self):
#         return self.title







# # about/models.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from datetime import date

# # =============================
# # 🌐 PAGE PRINCIPALE "À propos"
# # =============================
# class AboutPage(models.Model):
#     title = models.CharField(_("Titre"), max_length=200)
#     content = models.TextField(_("Contenu"))
#     mission = models.TextField(blank=True, null=True)
#     vision = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         verbose_name = _("À propos")
#         verbose_name_plural = _("À propos")

#     def __str__(self):
#         return self.title


# # =============================
# # 🧩 SECTIONS DYNAMIQUES
# # =============================
# class AboutSection(models.Model):
#     SECTION_CHOICES = [
#         ('mission', _("Mission")),
#         ('vision', _("Vision")),
#         ('team', _("Équipe")),
#         ('history', _("Histoire")),
#         ('values', _("Nos valeurs")),
#     ]

#     title = models.CharField(_("Titre"), max_length=200)
#     content = models.TextField(_("Contenu"))
#     section_type = models.CharField(_("Type de section"), max_length=20, choices=SECTION_CHOICES)
#     image = models.ImageField(_("Image"), upload_to="about/images/", blank=True, null=True)
#     order = models.PositiveIntegerField(_("Ordre"), default=0)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         verbose_name = _("Section À propos")
#         verbose_name_plural = _("Sections À propos")
#         ordering = ['order']

#     def __str__(self):
#         return f"{self.get_section_type_display()}: {self.title}"

#     def image_url(self):
#         return self.image.url if self.image else "/static/about/img/default_section.png"


# # =============================
# # 👥 ÉQUIPE
# # =============================
# class TeamMember(models.Model):
#     name = models.CharField(_("Nom"), max_length=100)
#     role = models.CharField(_("Rôle"), max_length=100)
#     photo = models.ImageField(_("Photo"), upload_to="about/images/", blank=True, null=True)
#     order = models.PositiveIntegerField(_("Ordre"), default=0)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         verbose_name = _("Membre de l'équipe")
#         verbose_name_plural = _("Membres de l'équipe")
#         ordering = ['order']

#     def __str__(self):
#         return self.name

#     def photo_url(self):
#         return self.photo.url if self.photo else "/static/about/img/default_team.png"


# # =============================
# # 🤝 PARTENAIRES
# # =============================
# class Partner(models.Model):
#     name = models.CharField(_("Nom"), max_length=100)
#     logo = models.ImageField(_("Logo"), upload_to="about/images/", blank=True, null=True)
#     website = models.URLField(_("Site web"), blank=True, null=True)
#     order = models.PositiveIntegerField(_("Ordre"), default=0)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         verbose_name = _("Partenaire")
#         verbose_name_plural = _("Partenaires")
#         ordering = ['order']

#     def __str__(self):
#         return self.name

#     def logo_url(self):
#         return self.logo.url if self.logo else "/static/about/img/default_partner.png"


# # =============================
# # 👶 ENFANTS
# # =============================
# class Child(models.Model):
#     GENDER_CHOICES = (
#         ('M', _('Garçon')),
#         ('F', _('Fille')),
#     )

#     name = models.CharField(_("Nom complet"), max_length=200)
#     gender = models.CharField(_("Sexe"), max_length=1, choices=GENDER_CHOICES, default='M')
#     photo = models.ImageField(_("Photo"), upload_to="children/", blank=True, null=True)
#     registration_number = models.CharField(_("N° d’enregistrement"), max_length=50, unique=True)
#     date_of_birth = models.DateField(_("Date de naissance"), null=True, blank=True)
#     school = models.CharField(_("École fréquentée"), max_length=255, blank=True)
#     short_story = models.TextField(_("Petite histoire / description"), blank=True)
#     is_active = models.BooleanField(_("Actif"), default=True)
#     created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
#     updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

#     class Meta:
#         verbose_name = _("Enfant")
#         verbose_name_plural = _("Enfants")
#         ordering = ["name"]

#     def __str__(self):
#         return self.name

#     @property
#     def age(self):
#         if self.date_of_birth:
#             today = date.today()
#             return today.year - self.date_of_birth.year - (
#                 (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
#             )
#         return None

#     def photo_url(self):
#         if self.photo:
#             return self.photo.url
#         return "/static/about/img/default_female.png" if self.gender == "F" else "/static/about/img/default_male.png"


# # =============================
# # SPONSORS ET DONS
# # =============================
# class Sponsor(models.Model):
#     name = models.CharField(_("Nom"), max_length=100)
#     email = models.EmailField(_("Email"), blank=True, null=True)

#     class Meta:
#         verbose_name = _("Parrain / Sponsor")
#         verbose_name_plural = _("Parrains / Sponsors")

#     def __str__(self):
#         return self.name or _("Anonyme")


# class ChildDonation(models.Model):
#     child = models.ForeignKey(
#         Child,
#         on_delete=models.CASCADE,
#         related_name="donations",
#         verbose_name=_("Enfant"),
#     )
#     sponsor = models.ForeignKey(
#         Sponsor,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         verbose_name=_("Sponsor"),
#     )
#     amount = models.DecimalField(_("Montant (FCFA)"), max_digits=10, decimal_places=2)
#     date = models.DateField(_("Date du don"), auto_now_add=True)

#     class Meta:
#         verbose_name = _("Don")
#         verbose_name_plural = _("Dons")
#         ordering = ["-date"]

#     def __str__(self):
#         sponsor_name = self.sponsor.name if self.sponsor else _("Anonyme")
#         return f"{sponsor_name} → {self.child.name} ({self.amount} FCFA)"


# # =============================
# # 🤱 MAMANS
# # =============================
# class Mother(models.Model):
#     name = models.CharField(_("Nom"), max_length=100)
#     registration_number = models.CharField(_("N° d’enregistrement"), max_length=50, unique=True)
#     story = models.TextField(_("Histoire / description"), blank=True)
#     photo = models.ImageField(_("Photo"), upload_to='mothers/', blank=True, null=True)
#     is_active = models.BooleanField(_("Actif"), default=True)
#     created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
#     updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

#     class Meta:
#         verbose_name = _("Maman")
#         verbose_name_plural = _("Mamans")
#         ordering = ['name']

#     def __str__(self):
#         return self.name

#     def photo_url(self):
#         return self.photo.url if self.photo else "/static/about/img/default_female.png"


# # =============================
# # 🎯 OBJECTIFS
# # =============================
# class Objective(models.Model):
#     title = models.CharField(_("Titre"), max_length=200)
#     description = models.TextField(_("Description"))
#     order = models.PositiveIntegerField(_("Ordre"), default=0)
#     is_active = models.BooleanField(_("Actif"), default=True)
#     created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
#     updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

#     class Meta:
#         verbose_name = _("Objectif")
#         verbose_name_plural = _("Objectifs")
#         ordering = ['order']

#     def __str__(self):
#         return self.title




# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from datetime import date

# # =============================
# # 🌐 PAGE PRINCIPALE "À propos"
# # =============================
# class AboutPage(models.Model):
#     title = models.CharField(_("Titre"), max_length=200)
#     content = models.TextField(_("Contenu"))
#     mission = models.TextField(blank=True, null=True)
#     vision = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         verbose_name = _("À propos")
#         verbose_name_plural = _("À propos")

#     def __str__(self):
#         return self.title


# # =============================
# # 🧩 SECTIONS DYNAMIQUES
# # =============================
# class AboutSection(models.Model):
#     SECTION_CHOICES = [
#         ('mission', _("Mission")),
#         ('vision', _("Vision")),
#         ('team', _("Équipe")),
#         ('history', _("Histoire")),
#         ('values', _("Nos valeurs")),
#     ]

#     title = models.CharField(_("Titre"), max_length=200)
#     content = models.TextField(_("Contenu"))
#     section_type = models.CharField(_("Type de section"), max_length=20, choices=SECTION_CHOICES)
#     image = models.ImageField(_("Image"), upload_to="about/images/", blank=True, null=True)
#     order = models.PositiveIntegerField(_("Ordre"), default=0)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         verbose_name = _("Section À propos")
#         verbose_name_plural = _("Sections À propos")
#         ordering = ['order']

#     def __str__(self):
#         return f"{self.get_section_type_display()}: {self.title}"


# # =============================
# # 👥 ÉQUIPE
# # =============================
# class TeamMember(models.Model):
#     name = models.CharField(_("Nom"), max_length=100)
#     role = models.CharField(_("Rôle"), max_length=100)
#     photo = models.ImageField(_("Photo"), upload_to="about/images/")
#     order = models.PositiveIntegerField(_("Ordre"), default=0)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         verbose_name = _("Membre de l'équipe")
#         verbose_name_plural = _("Membres de l'équipe")
#         ordering = ['order']

#     def __str__(self):
#         return self.name


# # =============================
# # 🤝 PARTENAIRES
# # =============================
# class Partner(models.Model):
#     name = models.CharField(_("Nom"), max_length=100)
#     logo = models.ImageField(_("Logo"), upload_to="about/images/")
#     website = models.URLField(_("Site web"), blank=True, null=True)
#     order = models.PositiveIntegerField(_("Ordre"), default=0)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         verbose_name = _("Partenaire")
#         verbose_name_plural = _("Partenaires")
#         ordering = ['order']

#     def __str__(self):
#         return self.name


# # =============================
# # 👶 ENFANTS
# # =============================
# class Child(models.Model):
#     GENDER_CHOICES = (
#         ('M', _('Garçon')),
#         ('F', _('Fille')),
#     )

#     name = models.CharField(_("Nom complet"), max_length=200)
#     gender = models.CharField(_("Sexe"), max_length=1, choices=GENDER_CHOICES, default='M')
#     photo = models.ImageField(_("Photo"), upload_to="children/", blank=True, null=True)
#     registration_number = models.CharField(_("N° d’enregistrement"), max_length=50, unique=True)
#     date_of_birth = models.DateField(_("Date de naissance"), null=True, blank=True)
#     school = models.CharField(_("École fréquentée"), max_length=255, blank=True)
#     short_story = models.TextField(_("Petite histoire / description"), blank=True)
#     is_active = models.BooleanField(_("Actif"), default=True)
#     created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
#     updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

#     class Meta:
#         verbose_name = _("Enfant")
#         verbose_name_plural = _("Enfants")
#         ordering = ["name"]

#     def __str__(self):
#         return self.name

#     @property
#     def age(self):
#         if self.date_of_birth:
#             today = date.today()
#             return today.year - self.date_of_birth.year - (
#                 (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
#             )
#         return None

#     def photo_url(self):
#         if self.photo:
#             return self.photo.url
#         return "/static/about/img/default_female.png" if self.gender == "F" else "/static/about/img/default_male.png"


# # =============================
# # SPONSORS ET DONS
# # =============================
# # class Sponsor(models.Model):
# #     name = models.CharField(_("Nom"), max_length=100)
# #     email = models.EmailField(_("Email"), blank=True, null=True)

# #     def __str__(self):
# #         return self.name or "Anonyme"

# # class ChildDonation(models.Model):
# #     child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='donations')
# #     sponsor = models.ForeignKey(Sponsor, on_delete=models.SET_NULL, null=True, blank=True)
# #     amount = models.DecimalField(_("Montant"), max_digits=10, decimal_places=2)
# #     date = models.DateField(_("Date du don"), auto_now_add=True)

# #     class Meta:
# #         verbose_name = _("Don")
# #         verbose_name_plural = _("Dons")

# #     def __str__(self):
# #         return f"{self.child.name} - {self.amount} FCFA"

# # =============================
# # SPONSORS ET DONS
# # =============================
# class Sponsor(models.Model):
#     name = models.CharField(_("Nom"), max_length=100)
#     email = models.EmailField(_("Email"), blank=True, null=True)

#     class Meta:
#         verbose_name = _("Parrain / Sponsor")
#         verbose_name_plural = _("Parrains / Sponsors")

#     def __str__(self):
#         return self.name or _("Anonyme")


# class ChildDonation(models.Model):
#     child = models.ForeignKey(
#         Child,
#         on_delete=models.CASCADE,
#         related_name="donations",
#         verbose_name=_("Enfant"),
#     )
#     sponsor = models.ForeignKey(
#         Sponsor,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         verbose_name=_("Sponsor"),
#     )
#     amount = models.DecimalField(_("Montant (FCFA)"), max_digits=10, decimal_places=2)
#     date = models.DateField(_("Date du don"), auto_now_add=True)

#     class Meta:
#         verbose_name = _("Don")
#         verbose_name_plural = _("Dons")
#         ordering = ["-date"]

#     def __str__(self):
#         sponsor_name = self.sponsor.name if self.sponsor else _("Anonyme")
#         return f"{sponsor_name} → {self.child.name} ({self.amount} FCFA)"


# # =============================
# # 🤱 MAMANS
# # =============================
# class Mother(models.Model):
#     name = models.CharField(_("Nom"), max_length=100)
#     registration_number = models.CharField(_("N° d’enregistrement"), max_length=50, unique=True)
#     story = models.TextField(_("Histoire / description"), blank=True)
#     photo = models.ImageField(_("Photo"), upload_to='mothers/', blank=True, null=True)
#     is_active = models.BooleanField(_("Actif"), default=True)
#     created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
#     updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

#     class Meta:
#         verbose_name = _("Maman")
#         verbose_name_plural = _("Mamans")
#         ordering = ['name']

#     def __str__(self):
#         return self.name

#     @property
#     def age(self):
#         if hasattr(self, 'date_of_birth') and self.date_of_birth:
#             today = date.today()
#             return today.year - self.date_of_birth.year - (
#                 (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
#             )
#         return None

#     def photo_url(self):
#         if self.photo:
#             return self.photo.url
#         return "/static/about/img/default_female.png"


# # =============================
# # 🎯 OBJECTIFS
# # =============================
# class Objective(models.Model):
#     title = models.CharField(_("Titre"), max_length=200)
#     description = models.TextField(_("Description"))
#     order = models.PositiveIntegerField(_("Ordre"), default=0)
#     is_active = models.BooleanField(_("Actif"), default=True)
#     created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
#     updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

#     class Meta:
#         verbose_name = _("Objectif")
#         verbose_name_plural = _("Objectifs")
#         ordering = ['order']

#     def __str__(self):
#         return self.title





# # about/models.py

# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from django.utils import timezone
# from datetime import date



# # =============================
# # 🌐 PAGE PRINCIPALE "À propos"
# # =============================
# class AboutPage(models.Model):
#     title = models.CharField(_("Titre"), max_length=200)
#     content = models.TextField(_("Contenu"))
#     mission = models.TextField(blank=True, null=True)
#     vision = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         verbose_name = _("À propos")
#         verbose_name_plural = _("À propos")

#     def __str__(self):
#         return self.title


# # =============================
# # 🧩 SECTIONS DYNAMIQUES
# # =============================
# class AboutSection(models.Model):
#     SECTION_CHOICES = [
#         ('mission', _("Mission")),
#         ('vision', _("Vision")),
#         ('team', _("Équipe")),
#         ('history', _("Histoire")),
#         ('values', _("Nos valeurs")),
#     ]

#     title = models.CharField(_("Titre"), max_length=200)
#     content = models.TextField(_("Contenu"))
#     section_type = models.CharField(
#         _("Type de section"), max_length=20, choices=SECTION_CHOICES
#     )
#     image = models.ImageField(_("Image"), upload_to="about/images/", blank=True, null=True)
#     order = models.PositiveIntegerField(_("Ordre"), default=0)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         verbose_name = _("Section À propos")
#         verbose_name_plural = _("Sections À propos")
#         ordering = ['order']

#     def __str__(self):
#         return f"{self.get_section_type_display()}: {self.title}"


# # =============================
# # 👥 ÉQUIPE
# # =============================
# class TeamMember(models.Model):
#     name = models.CharField(_("Nom"), max_length=100)
#     role = models.CharField(_("Rôle"), max_length=100)
#     photo = models.ImageField(_("Photo"), upload_to="about/images/")
#     order = models.PositiveIntegerField(_("Ordre"), default=0)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         verbose_name = _("Membre de l'équipe")
#         verbose_name_plural = _("Membres de l'équipe")
#         ordering = ['order']

#     def __str__(self):
#         return self.name


# # =============================
# # 🤝 PARTENAIRES
# # =============================
# class Partner(models.Model):
#     name = models.CharField(_("Nom"), max_length=100)
#     logo = models.ImageField(_("Logo"), upload_to="about/images/")
#     website = models.URLField(_("Site web"), blank=True, null=True)
#     order = models.PositiveIntegerField(_("Ordre"), default=0)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         verbose_name = _("Partenaire")
#         verbose_name_plural = _("Partenaires")
#         ordering = ['order']

#     def __str__(self):
#         return self.name


# # =============================
# # 👶 ENFANTS
# # =============================

# class Child(models.Model):
#     GENDER_CHOICES = (
#         ('M', _('Garçon')),
#         ('F', _('Fille')),
#     )

#     name = models.CharField(max_length=200, verbose_name=_("Nom complet"))
#     gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M', verbose_name=_("Sexe"))
#     photo = models.ImageField(upload_to="children/", blank=True, null=True, verbose_name=_("Photo"))
#     registration_number = models.CharField(max_length=50, unique=True, verbose_name=_("N° d’enregistrement"))
#     date_of_birth = models.DateField(null=True, blank=True, verbose_name=_("Date de naissance"))
#     school = models.CharField(max_length=255, blank=True, verbose_name=_("École fréquentée"))
#     short_story = models.TextField(blank=True, verbose_name=_("Petite histoire / description"))
#     is_active = models.BooleanField(default=True, verbose_name=_("Actif"))
#     created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Créé le"))

#     class Meta:
#         verbose_name = _("Enfant")
#         verbose_name_plural = _("Enfants")
#         ordering = ["name"]

#     def __str__(self):
#         return f"{self.name}"

#     # 🔹 Calcul automatique de l'âge
#     @property
#     def age(self):
#         if self.date_of_birth:
#             today = date.today()
#             return today.year - self.date_of_birth.year - (
#                 (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
#             )
#         return None

#     # 🔹 Photo avec silhouette par défaut
#     def photo_url(self):
#         if self.photo:
#             return self.photo.url
#         if self.gender == "F":
#             return "/static/about/img/default_female.png"
#         return "/static/about/img/default_male.png"
    
# class Sponsor(models.Model):
#     name = models.CharField(max_length=100)
#     email = models.EmailField(blank=True, null=True)

# class ChildDonation(models.Model):
#     child = models.ForeignKey('Child', on_delete=models.CASCADE, related_name='donations')
#     sponsor = models.ForeignKey(Sponsor, on_delete=models.SET_NULL, null=True, blank=True)
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     date = models.DateField(auto_now_add=True)        
# # =============================
# # 🤱 MAMANS
# # =============================
# class Mother(models.Model):
#     name = models.CharField(max_length=100)
#     registration_number = models.CharField(max_length=50, unique=True)
#     story = models.TextField()
#     photo = models.ImageField(upload_to='mothers/')
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         verbose_name = _("Maman")
#         verbose_name_plural = _("Mamans")
#         ordering = ['name']

#     def __str__(self):
#         return self.name


# # =============================
# # 🎯 OBJECTIFS
# # =============================
# class Objective(models.Model):
#     title = models.CharField(max_length=200)
#     description = models.TextField()
#     order = models.PositiveIntegerField(default=0)
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         verbose_name = _("Objectif")
#         verbose_name_plural = _("Objectifs")
#         ordering = ['order']

#     def __str__(self):
#         return self.title




# #about/models.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _

# class AboutPage(models.Model):
#     title = models.CharField(_("Titre"), max_length=200)
#     content = models.TextField(_("Contenu"))
#     created_at = models.DateTimeField(auto_now_add=True)
#     mission = models.TextField(blank=True, null=True)
#     vision = models.TextField(blank=True, null=True)
#     class Meta:
#         verbose_name = _("À propos")
#         verbose_name_plural = _("À propos")

#     def __str__(self):
#         return self.title

# class AboutSection(models.Model):
#     SECTION_CHOICES = [
#         ('mission', _("Mission")),
#         ('vision', _("Vision")),
#         ('team', _("Équipe")),
#         ('history', _("Histoire")),
#         ('values', _("Nos valeurs")),

#     ]

#     title = models.CharField(_("Titre"), max_length=200)
#     content = models.TextField(_("Contenu"))
#     section_type = models.CharField(
#         _("Type de section"), max_length=20, choices=SECTION_CHOICES
#     )
#     image = models.ImageField(_("Image"), upload_to="about/images/", blank=True, null=True)
#     order = models.PositiveIntegerField(_("Ordre"), default=0)

#     class Meta:
#         verbose_name = _("Section À propos")
#         verbose_name_plural = _("Sections À propos")
#         ordering = ['order']

#     def __str__(self):
#         return f"{self.get_section_type_display()}: {self.title}"

# class TeamMember(models.Model):
#     name = models.CharField(_("Nom"), max_length=100)
#     role = models.CharField(_("Rôle"), max_length=100)
#     photo = models.ImageField(_("Photo"), upload_to="about/images/")
#     order = models.PositiveIntegerField(_("Ordre"), default=0)

#     class Meta:
#         verbose_name = _("Membre de l'équipe")
#         verbose_name_plural = _("Membres de l'équipe")
#         ordering = ['order']

#     def __str__(self):
#         return self.name


# class Partner(models.Model):
#     name = models.CharField(_("Nom"), max_length=100)
#     logo = models.ImageField(_("Logo"), upload_to="about/images/")
#     website = models.URLField(_("Site web"), blank=True, null=True)
#     order = models.PositiveIntegerField(_("Ordre"), default=0)

#     class Meta:
#         verbose_name = _("Partenaire")
#         verbose_name_plural = _("Partenaires")
#         ordering = ['order']

#     def __str__(self):
#         return self.name
    
# class Child(models.Model):
#     name = models.CharField(max_length=100)
#     registration_number = models.CharField(max_length=50, unique=True)
#     school = models.CharField(max_length=100)
#     story = models.TextField()
#     photo = models.ImageField(upload_to='children/')
#     active = models.BooleanField(default=True)

# class Mother(models.Model):
#     name = models.CharField(max_length=100)
#     registration_number = models.CharField(max_length=50, unique=True)
#     story = models.TextField()
#     photo = models.ImageField(upload_to='mothers/')
#     active = models.BooleanField(default=True)
