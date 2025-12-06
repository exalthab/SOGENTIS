# about/models/about_page.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields

class AboutPage(TranslatableModel):
    translations = TranslatedFields(
        title=models.CharField(_("Titre"), max_length=200),
        content=models.TextField(_("Contenu"), blank=True),
    )

    cover_photo = models.ImageField(
        _("Photo de couverture"),
        upload_to="about/cover/",
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

    class Meta:
        verbose_name = _("Page À propos")
        verbose_name_plural = _("Pages À propos")

    def __str__(self):
        return self.safe_translation_getter("title", any_language=True) or _("À propos")












# # about/models/about_page.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from parler.models import TranslatableModel, TranslatedFields

# class AboutPage(TranslatableModel):
#     translations = TranslatedFields(
#         title=models.CharField(_("Titre"), max_length=200),
#         content=models.TextField(_("Contenu"), blank=True),
#     )
#     cover_photo = models.ImageField(
#         _("Photo de couverture"),
#         upload_to="about/cover/",
#         blank=True,
#         null=True
#     )
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         verbose_name = _("Page À propos")
#         verbose_name_plural = _("Pages À propos")

#     def __str__(self):
#         return self.safe_translation_getter("title", any_language=True) or "À propos"





# # about/models/about_page.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from parler.models import TranslatableModel, TranslatedFields


# class AboutPage(TranslatableModel):
#     translations = TranslatedFields(
#         title=models.CharField(_("Titre"), max_length=200),
#         content=models.TextField(_("Contenu"), blank=True),
#     )
#     cover_photo = models.ImageField(_("Photo de couverture"), upload_to="about/cover/", blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         verbose_name = _("Page À propos")
#         verbose_name_plural = _("Pages À propos")

#     def __str__(self):
#         return self.safe_translation_getter("title", any_language=True) or "À propos"




    
# class AboutPage(TranslatableModel):
#     translations = TranslatedFields(
#         title=models.CharField(max_length=200),
#         content=models.TextField(blank=True),
#     )
#     cover_photo = models.ImageField(upload_to="about/cover/", blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.safe_translation_getter("title", any_language=True) or "À propos"


# # --- SECTIONS DYNAMIQUES --- #

# class MissionItem(TranslatableModel):
#     translations = TranslatedFields(
#         title=models.CharField(max_length=150),
#         description=models.TextField(blank=True),
#     )
#     about_page = models.ForeignKey(
#         "about.AboutPage",
#         related_name="missions",
#         on_delete=models.CASCADE,
#         verbose_name="Page À propos"
#     )
#     icon = models.CharField(
#         max_length=100,
#         blank=True,
#         help_text="Nom d’icône FontAwesome (ex: fa-solid fa-hands-helping)"
#     )
#     image = models.ImageField(upload_to="about/missions/", blank=True, null=True)
#     order = models.PositiveIntegerField(default=0)

#     class Meta:
#         ordering = ["order"]
#         verbose_name = "Mission"
#         verbose_name_plural = "Missions"

#     def __str__(self):
#         return self.safe_translation_getter("title", any_language=True)


# class VisionItem(TranslatableModel):
#     translations = TranslatedFields(
#         title=models.CharField(max_length=150),
#         description=models.TextField(blank=True),
#     )
#     about_page = models.ForeignKey(
#         "about.AboutPage",
#         related_name="visions",
#         on_delete=models.CASCADE,
#         verbose_name="Page À propos"
#     )
#     icon = models.CharField(max_length=100, blank=True)
#     image = models.ImageField(upload_to="about/visions/", blank=True, null=True)
#     order = models.PositiveIntegerField(default=0)

#     class Meta:
#         ordering = ["order"]
#         verbose_name = "Vision"
#         verbose_name_plural = "Visions"

#     def __str__(self):
#         return self.safe_translation_getter("title", any_language=True)


# class ValueItem(TranslatableModel):
#     translations = TranslatedFields(
#         title=models.CharField(max_length=150),
#         description=models.TextField(blank=True),
#     )
#     about_page = models.ForeignKey(
#         "about.AboutPage",
#         related_name="values",
#         on_delete=models.CASCADE,
#         verbose_name="Page À propos"
#     )
#     icon = models.CharField(max_length=100, blank=True)
#     image = models.ImageField(upload_to="about/values/", blank=True, null=True)
#     order = models.PositiveIntegerField(default=0)

#     class Meta:
#         ordering = ["order"]
#         verbose_name = "Valeur"
#         verbose_name_plural = "Valeurs"

#     def __str__(self):
#         return self.safe_translation_getter("title", any_language=True)


# class ObjectiveItem(TranslatableModel):
#     translations = TranslatedFields(
#         title=models.CharField(max_length=150),
#         description=models.TextField(blank=True),
#     )
#     about_page = models.ForeignKey(
#         "about.AboutPage",
#         related_name="objectives",
#         on_delete=models.CASCADE,
#         verbose_name="Page À propos"
#     )
#     icon = models.CharField(max_length=100, blank=True)
#     image = models.ImageField(upload_to="about/objectives/", blank=True, null=True)
#     order = models.PositiveIntegerField(default=0)

#     class Meta:
#         ordering = ["order"]
#         verbose_name = "Objectif"
#         verbose_name_plural = "Objectifs"

#     def __str__(self):
#         return self.safe_translation_getter("title", any_language=True)




# from django.db import models
# from parler.models import TranslatableModel, TranslatedFields


# class AboutPage(TranslatableModel):
#     translations = TranslatedFields(
#         title=models.CharField(max_length=200),
#         content=models.TextField(blank=True),
#     )
#     cover_photo = models.ImageField(upload_to="about/cover/", blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.safe_translation_getter("title", any_language=True) or "À propos"


# # --- SECTIONS DYNAMIQUES --- #

# class MissionItem(TranslatableModel):
#     about_page = models.ForeignKey(AboutPage, related_name="missions", on_delete=models.CASCADE)
#     translations = TranslatedFields(
#         title=models.CharField(max_length=150),
#         description=models.TextField(blank=True),
#     )
#     icon = models.CharField(max_length=100, blank=True, help_text="Nom d’icône FontAwesome (ex: fa-solid fa-hands-helping)")
#     image = models.ImageField(upload_to="about/missions/", blank=True, null=True)
#     order = models.PositiveIntegerField(default=0)

#     class Meta:
#         ordering = ["order"]

#     def __str__(self):
#         return self.safe_translation_getter("title", any_language=True)


# class VisionItem(TranslatableModel):
#     about_page = models.ForeignKey(AboutPage, related_name="visions", on_delete=models.CASCADE)
#     translations = TranslatedFields(
#         title=models.CharField(max_length=150),
#         description=models.TextField(blank=True),
#     )
#     icon = models.CharField(max_length=100, blank=True)
#     image = models.ImageField(upload_to="about/visions/", blank=True, null=True)
#     order = models.PositiveIntegerField(default=0)

#     class Meta:
#         ordering = ["order"]

#     def __str__(self):
#         return self.safe_translation_getter("title", any_language=True)


# class ValueItem(TranslatableModel):
#     about_page = models.ForeignKey(AboutPage, related_name="values", on_delete=models.CASCADE)
#     translations = TranslatedFields(
#         title=models.CharField(max_length=150),
#         description=models.TextField(blank=True),
#     )
#     icon = models.CharField(max_length=100, blank=True)
#     image = models.ImageField(upload_to="about/values/", blank=True, null=True)
#     order = models.PositiveIntegerField(default=0)

#     class Meta:
#         ordering = ["order"]

#     def __str__(self):
#         return self.safe_translation_getter("title", any_language=True)


# class ObjectiveItem(TranslatableModel):
#     about_page = models.ForeignKey(AboutPage, related_name="objectives", on_delete=models.CASCADE)
#     translations = TranslatedFields(
#         title=models.CharField(max_length=150),
#         description=models.TextField(blank=True),
#     )
#     icon = models.CharField(max_length=100, blank=True)
#     image = models.ImageField(upload_to="about/objectives/", blank=True, null=True)
#     order = models.PositiveIntegerField(default=0)

#     class Meta:
#         ordering = ["order"]

#     def __str__(self):
#         return self.safe_translation_getter("title", any_language=True)






# # about/models/about_page.py
# from django.db import models
# from parler.models import TranslatableModel, TranslatedFields

# class AboutPage(TranslatableModel):
#     translations = TranslatedFields(
#         title=models.CharField(max_length=200),
#         content=models.TextField(blank=True),
#     )
#     cover_photo = models.ImageField(upload_to="about/cover/", blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         verbose_name = "Page À propos"
#         verbose_name_plural = "Pages À propos"

#     def __str__(self):
#         return self.safe_translation_getter("title", any_language=True) or "Page À propos"


# class MissionItem(TranslatableModel):
#     about_page = models.ForeignKey(
#         AboutPage, on_delete=models.CASCADE, related_name="missions"
#     )
#     translations = TranslatedFields(
#         title=models.CharField("Titre", max_length=150),
#         description=models.TextField("Description", blank=True),
#     )
#     icon = models.CharField("Icône (classe CSS ou nom)", max_length=100, blank=True)
#     image = models.ImageField(upload_to="about/mission/", blank=True, null=True)
#     order = models.PositiveIntegerField(default=0)

#     class Meta:
#         ordering = ["order"]
#         verbose_name = "Mission"
#         verbose_name_plural = "Missions"

#     def __str__(self):
#         return self.safe_translation_getter("title", any_language=True)


# class VisionItem(TranslatableModel):
#     about_page = models.ForeignKey(
#         AboutPage, on_delete=models.CASCADE, related_name="visions"
#     )
#     translations = TranslatedFields(
#         title=models.CharField("Titre", max_length=150),
#         description=models.TextField("Description", blank=True),
#     )
#     icon = models.CharField("Icône (classe CSS ou nom)", max_length=100, blank=True)
#     image = models.ImageField(upload_to="about/vision/", blank=True, null=True)
#     order = models.PositiveIntegerField(default=0)

#     class Meta:
#         ordering = ["order"]
#         verbose_name = "Vision"
#         verbose_name_plural = "Visions"

#     def __str__(self):
#         return self.safe_translation_getter("title", any_language=True)





# # about/models/about_page.py
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from parler.models import TranslatableModel, TranslatedFields



# class AboutPage(TranslatableModel):
#     translations = TranslatedFields(
#         title=models.CharField("Titre", max_length=200),
#         content=models.TextField("Contenu"),
#         mission=models.TextField("Mission", blank=True, null=True),
#         vision=models.TextField("Vision", blank=True, null=True),
#     )
#     cover_photo = models.ImageField("Photo de couverture", upload_to="about/covers/", blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         verbose_name = "Page À propos"
#         verbose_name_plural = "Pages À propos"

#     def __str__(self):
#         return self.safe_translation_getter("title", any_language=True) or "(Sans titre)"




# class AboutPage(TranslatableModel):
#     translations = TranslatedFields(
#         title=models.CharField(_("Titre"), max_length=200),
#         content=models.TextField(_("Contenu")),
#         mission=models.TextField(_("Mission"), blank=True, null=True),
#         vision=models.TextField(_("Vision"), blank=True, null=True),
#     )
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         verbose_name = _("À propos")
#         verbose_name_plural = _("À propos")

#     def __str__(self):
#         return self.safe_translation_getter("title", any_language=True) or _("(Sans titre)")



# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from parler.models import TranslatableModel, TranslatedFields


# class AboutPage(TranslatableModel):
#     translations = TranslatedFields(
#         title=models.CharField(_("Titre"), max_length=200),
#         content=models.TextField(_("Contenu")),
#         mission=models.TextField(_("Mission"), blank=True, null=True),
#         vision=models.TextField(_("Vision"), blank=True, null=True),
#     )
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         verbose_name = _("À propos")
#         verbose_name_plural = _("À propos")

#     def __str__(self):
#         return self.safe_translation_getter("title", any_language=True) or _("(Sans titre)")


# class AboutPage(models.Model):
#     title = models.CharField(_("Titre principal"), max_length=255)
#     subtitle = models.CharField(_("Sous-titre"), max_length=255, blank=True)
#     description = models.TextField(_("Description"), blank=True)
#     cover_image = models.ImageField(
#         _("Image de couverture"), upload_to="about/cover/", blank=True, null=True
#     )
#     last_updated = models.DateTimeField(_("Dernière mise à jour"), auto_now=True)

#     class Meta:
#         verbose_name = _("Page À propos")
#         verbose_name_plural = _("Pages À propos")

#     def __str__(self):
#         return self.title
