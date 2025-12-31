from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from accounts_users.models.custom_users import CustomUser
from accounts_users.models.users_economic_profile import UserProfile

from accounts_users.services.profile_update_service import update_user_profile


class ProfileUpdateServiceTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="test@example.com",
            password="testpass"
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            phone="+33123456789"
        )

    # --------------------------------------------------
    # 1️⃣ Mise à jour avec user + data simples
    # --------------------------------------------------
    def test_update_with_user_and_data_only(self):
        data = {
            "first_name": "Jean",
            "last_name": "Dupont",
            "phone": "+33612345678",
        }

        profile = update_user_profile(self.user, data)

        self.assertEqual(profile.first_name, "Jean")
        self.assertEqual(profile.last_name, "Dupont")
        self.assertEqual(profile.phone, "+33612345678")

    # --------------------------------------------------
    # 2️⃣ Mise à jour avec instance profile + cleaned_data
    # --------------------------------------------------
    def test_update_with_profile_and_cleaned_data(self):
        cleaned_data = {
            "first_name": "Alice",
            "last_name": "Martin",
            "phone": "+33765432100",
        }

        profile = update_user_profile(self.profile, cleaned_data)

        self.assertEqual(profile.first_name, "Alice")
        self.assertEqual(profile.last_name, "Martin")
        self.assertEqual(profile.phone, "+33765432100")

    # --------------------------------------------------
    # 3️⃣ Mise à jour avec fichier autorisé (photo uniquement)
    # --------------------------------------------------
    def test_update_with_profile_picture_only(self):
        mock_picture = SimpleUploadedFile(
            "avatar.jpg",
            b"fake-image-data",
            content_type="image/jpeg"
        )

        files = {
            "profile_picture": mock_picture,
        }

        profile = update_user_profile(self.user, {}, files)

        self.assertTrue(profile.profile_picture)







# # accounts_users/tests/test_profile_update_service.py
# from django.test import TestCase
# from django.core.files.uploadedfile import SimpleUploadedFile

# from accounts_users.models.users import CustomUser
# from accounts_users.models.users_profile import UserProfile
# from accounts_users.models.membership_role import MembershipRole

# # ✅ IMPORT CORRECT (FICHIER EXISTANT)
# from accounts_users.services.profile_validation_service import update_user_profile


# class ProfileUpdateServiceTest(TestCase):

#     def setUp(self):
#         self.user = CustomUser.objects.create_user(
#             email="test@example.com",
#             password="testpass"
#         )
#         self.membership_role = MembershipRole.objects.create(
#             name="Membre",
#             description="Rôle test"
#         )
#         self.profile = UserProfile.objects.create(
#             user=self.user,
#             phone="+33123456789"
#         )

#     # --------------------------------------------------
#     # 1️⃣ Mise à jour avec user + data simples
#     # --------------------------------------------------
#     def test_update_with_user_and_data_only(self):
#         data = {
#             "first_name": "Jean",
#             "last_name": "Dupont",
#             "phone": "+33612345678",
#             # "country_of_residence": "FR",
#             "message": "Bonjour",
#             "membership_role": self.membership_role.id,
#         }

#         profile = update_user_profile(self.user, data)

#         self.assertEqual(profile.first_name, "Jean")
#         self.assertEqual(profile.last_name, "Dupont")
#         self.assertEqual(profile.phone, "+33612345678")
#         # self.assertEqual(profile.country_of_residence, "FR")
#         self.assertEqual(profile.message, "Bonjour")
#         self.assertEqual(profile.membership_role, self.membership_role)

#     # --------------------------------------------------
#     # 2️⃣ Mise à jour avec instance profile + cleaned_data
#     # --------------------------------------------------
#     def test_update_with_profile_and_cleaned_data(self):
#         cleaned_data = {
#             "first_name": "Alice",
#             "last_name": "Martin",
#             "phone": "+33765432100",
#             "country_of_birth": "BE",
#             "message": "Test",
#         }

#         profile = update_user_profile(self.profile, cleaned_data)

#         self.assertEqual(profile.first_name, "Alice")
#         self.assertEqual(profile.last_name, "Martin")
#         self.assertEqual(profile.phone, "+33765432100")
#         # self.assertEqual(profile.country_of_birth, "BE")

#     # --------------------------------------------------
#     # 3️⃣ Mise à jour avec fichiers
#     # --------------------------------------------------
#     def test_update_with_files(self):
#         mock_picture = SimpleUploadedFile(
#             "avatar.jpg",
#             b"fake-image-data",
#             content_type="image/jpeg"
#         )
#         mock_record = SimpleUploadedFile(
#             "casier.pdf",
#             b"fake-pdf-data",
#             content_type="application/pdf"
#         )

#         data = {
#             "first_name": "Louis",
#             "last_name": "Lemoine",
#         }

#         files = {
#             "profile_picture": mock_picture,
#             "judicial_record": mock_record,
#         }

#         profile = update_user_profile(self.user, data, files)

#         self.assertTrue(profile.profile_picture)
#         self.assertTrue(profile.judicial_record)







# # accounts_users/tests/test_profile_update_service.py
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
