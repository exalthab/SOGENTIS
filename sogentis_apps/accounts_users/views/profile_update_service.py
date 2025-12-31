# accounts_users/services/profile_update_service.py

from django.core.exceptions import ObjectDoesNotExist
from accounts_users.models.users_economic_profile import UserProfile


def update_user_profile(user_or_profile, data, files=None):
    """
    Mise à jour STRICTE du UserProfile.
    ⚠️ Ne touche JAMAIS aux données sociales (ONG).
    """

    # ------------------------------------------------------
    # 1️⃣ Récupération ou création du profil
    # ------------------------------------------------------
    if isinstance(user_or_profile, UserProfile):
        profile = user_or_profile
    else:
        try:
            profile = user_or_profile.userprofile
        except ObjectDoesNotExist:
            profile = UserProfile.objects.create(user=user_or_profile)

    # ------------------------------------------------------
    # 2️⃣ Champs AUTORISÉS (RÉELS)
    # ------------------------------------------------------
    allowed_fields = [
        # Identité
        "first_name",
        "last_name",
        "middle_names",
        "nickname",

        # Contact / pro
        "phone",
        "profession",
        "function",

        # Résidence
        "country_of_residence",
        "city_of_residence",
        "address",

        # Pays de naissance
        "country_of_birth",
    ]

    for field in allowed_fields:
        if field in data:
            setattr(profile, field, data[field])

    # ------------------------------------------------------
    # 3️⃣ FICHIER AUTORISÉ
    # ------------------------------------------------------
    if files and files.get("profile_picture"):
        profile.profile_picture = files["profile_picture"]

    # ------------------------------------------------------
    # 4️⃣ Sauvegarde
    # ------------------------------------------------------
    profile.save()
    return profile









# # accounts_users/views/profile_update_service.py 21/12/2025 error

# from django.core.exceptions import ObjectDoesNotExist

# from accounts_users.models.users_profile import UserProfile
# from accounts_users.models.membership_role import MembershipRole


# def update_user_profile(user_or_profile, data, files=None):
#     """
#     Service générique pour mettre à jour un profil utilisateur.

#     Compatible avec :
#     - update_user_profile(user, data)
#     - update_user_profile(profile, cleaned_data)
#     - update_user_profile(user, data, files)

#     Aligné STRICTEMENT avec le modèle UserProfile réel.
#     """

#     # ------------------------------------------------------
#     # 1️⃣ Récupération ou création du profil
#     # ------------------------------------------------------
#     if isinstance(user_or_profile, UserProfile):
#         profile = user_or_profile
#     else:
#         try:
#             profile = user_or_profile.userprofile
#         except ObjectDoesNotExist:
#             profile = UserProfile.objects.create(user=user_or_profile)

#     # ------------------------------------------------------
#     # 2️⃣ Champs autorisés (RÉELS)
#     # ------------------------------------------------------
#     allowed_fields = [
#         # Identité
#         "first_name",
#         "last_name",

#         # Contact
#         "phone",

#         # Pays (ISO alpha-2 UNIQUEMENT)
#         "country_of_residence",
#         "country_of_birth",

#         # Divers
#         "message",
#     ]

#     for field in allowed_fields:
#         if field in data:
#             setattr(profile, field, data[field])

#     # ------------------------------------------------------
#     # 3️⃣ Gestion du MembershipRole (FK)
#     # ------------------------------------------------------
#     if "membership_role" in data:
#         membership_role = data.get("membership_role")

#         if isinstance(membership_role, int):
#             try:
#                 profile.membership_role = MembershipRole.objects.get(id=membership_role)
#             except MembershipRole.DoesNotExist:
#                 pass

#         elif isinstance(membership_role, MembershipRole):
#             profile.membership_role = membership_role

#     # ------------------------------------------------------
#     # 4️⃣ Gestion des fichiers
#     # ------------------------------------------------------
#     if files:
#         if files.get("profile_picture"):
#             profile.profile_picture = files["profile_picture"]

#         if files.get("judicial_record"):
#             profile.judicial_record = files["judicial_record"]

#     # ------------------------------------------------------
#     # 5️⃣ Sauvegarde finale
#     # ------------------------------------------------------
#     profile.save()
#     return profile





# # accounts_users/views/profile_update_service.py November 2025

# from django.core.exceptions import ObjectDoesNotExist
# from accounts_users.models.users_profile import UserProfile, MembershipRole


# def update_user_profile(user_or_profile, data, files=None):
#     """
#     Service générique pour mettre à jour un profil utilisateur.
#     Compatible avec :
#     - update_user_profile(user, data)
#     - update_user_profile(profile, cleaned_data)
#     - update_user_profile(user, data, files)

#     Les tests fournis valident :
#     - Mise à jour simple des champs texte
#     - Mise à jour depuis cleaned_data
#     - Upload fichiers : profile_picture, judicial_record
#     """

#     # ------------------------------------------------------
#     # 1️⃣ Détermine si on a passé un User ou un UserProfile
#     # ------------------------------------------------------
#     if isinstance(user_or_profile, UserProfile):
#         profile = user_or_profile
#     else:
#         # Tu as passé un user → on récupère son profil
#         try:
#             profile = user_or_profile.userprofile
#         except ObjectDoesNotExist:
#             # On crée un profil s'il n'existe pas (sécurité)
#             profile = UserProfile.objects.create(user=user_or_profile)

#     # ------------------------------------------------------
#     # 2️⃣ Mise à jour des champs standards
#     # ------------------------------------------------------
#     allowed_fields = [
#         "full_name",
#         "phone",
#         # "country",
#         "message",
#         "role",                # rôle secondaire (texte libre)
#         "membership_role",     # FK vers MembershipRole
#     ]

#     for field in allowed_fields:
#         if field in data:
#             setattr(profile, field, data[field])

#     # ------------------------------------------------------
#     # 3️⃣ Gestion du MembershipRole (FK)
#     # ------------------------------------------------------
#     if "membership_role" in data:
#         membership_role = data.get("membership_role")

#         # Si l’input est un ID → récupérer l'objet
#         if isinstance(membership_role, int):
#             try:
#                 profile.membership_role = MembershipRole.objects.get(id=membership_role)
#             except MembershipRole.DoesNotExist:
#                 pass  # Tests n’exigent pas message d’erreur

#         # Si on reçoit directement un objet MembershipRole
#         elif isinstance(membership_role, MembershipRole):
#             profile.membership_role = membership_role

#     # ------------------------------------------------------
#     # 4️⃣ Gestion des fichiers
#     # ------------------------------------------------------
#     if files:
#         picture = files.get("profile_picture")
#         record = files.get("judicial_record")

#         if picture:
#             profile.profile_picture = picture

#         if record:
#             profile.judicial_record = record

#     # ------------------------------------------------------
#     # 5️⃣ Sauvegarde finale
#     # ------------------------------------------------------
#     profile.save()
#     return profile
















# # /accounts_users/views/profile_update_service.py
# from django.test import TestCase
# from django.core.files.uploadedfile import SimpleUploadedFile
# from accounts_users.models.users import CustomUser
# from accounts_users.models.users_profile import UserProfile, MembershipRole
# from accounts_users.views.profile_update_service import update_user_profile


# class ProfileUpdateServiceTest(TestCase):

#     def setUp(self):
#         self.user = CustomUser.objects.create_user(email="test@example.com", password="testpass")
#         self.membership_role = MembershipRole.objects.create(name="Membre", description="Rôle test")
#         self.profile = UserProfile.objects.create(user=self.user)

#     def test_update_with_user_and_data_only(self):
#         data = {
#             'full_name': 'Jean Dupont',
#             'phone': '+33612345678',
#             'country': 'France',
#             'message': 'Bonjour',
#             'membership_role': self.membership_role.id,
#             'role': 'demandeur',
#         }

#         profile = update_user_profile(self.user, data)

#         self.assertEqual(profile.full_name, 'Jean Dupont')
#         self.assertEqual(profile.phone, '+33612345678')
#         self.assertEqual(profile.country, 'France')
#         self.assertEqual(profile.message, 'Bonjour')
#         self.assertEqual(profile.membership_role, self.membership_role)
#         self.assertEqual(profile.role, 'demandeur')

#     def test_update_with_profile_and_cleaned_data(self):
#         cleaned_data = {
#             'full_name': 'Alice Martin',
#             'phone': '+33765432100',
#             'country': 'Belgique',
#             'message': 'Test',
#             'role': 'recruteur',
#             'judicial_record': None  # Peut être remplacé par un fichier
#         }

#         profile = update_user_profile(self.profile, cleaned_data)

#         self.assertEqual(profile.full_name, 'Alice Martin')
#         self.assertEqual(profile.phone, '+33765432100')
#         self.assertEqual(profile.country, 'Belgique')
#         self.assertEqual(profile.role, 'recruteur')

#     def test_update_with_files(self):
#         mock_picture = SimpleUploadedFile("avatar.jpg", b"fake-image-data", content_type="image/jpeg")
#         mock_record = SimpleUploadedFile("casier.pdf", b"fake-pdf-data", content_type="application/pdf")

#         data = {
#             'full_name': 'Louis Lemoine',
#         }

#         files = {
#             'profile_picture': mock_picture,
#             'judicial_record': mock_record,
#         }

#         profile = update_user_profile(self.user, data, files)

#         self.assertTrue(profile.profile_picture)
#         self.assertTrue(profile.judicial_record)
