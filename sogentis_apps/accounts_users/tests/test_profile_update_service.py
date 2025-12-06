from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts_users.models.users import CustomUser
from accounts_users.models.users_profile import UserProfile, MembershipRole
from accounts_users.profile_update_service import update_user_profile


class ProfileUpdateServiceTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(email="test@example.com", password="testpass")
        self.membership_role = MembershipRole.objects.create(name="Membre", description="Rôle test")
        self.profile = UserProfile.objects.create(user=self.user)

    def test_update_with_user_and_data_only(self):
        data = {
            'full_name': 'Jean Dupont',
            'phone': '+33612345678',
            'country': 'France',
            'message': 'Bonjour',
            'membership_role': self.membership_role.id,
            'role': 'demandeur',
        }

        profile = update_user_profile(self.user, data)

        self.assertEqual(profile.full_name, 'Jean Dupont')
        self.assertEqual(profile.phone, '+33612345678')
        self.assertEqual(profile.country, 'France')
        self.assertEqual(profile.message, 'Bonjour')
        self.assertEqual(profile.membership_role, self.membership_role)
        self.assertEqual(profile.role, 'demandeur')

    def test_update_with_profile_and_cleaned_data(self):
        cleaned_data = {
            'full_name': 'Alice Martin',
            'phone': '+33765432100',
            'country': 'Belgique',
            'message': 'Test',
            'role': 'recruteur',
            'judicial_record': None  # Peut être remplacé par un fichier
        }

        profile = update_user_profile(self.profile, cleaned_data)

        self.assertEqual(profile.full_name, 'Alice Martin')
        self.assertEqual(profile.phone, '+33765432100')
        self.assertEqual(profile.country, 'Belgique')
        self.assertEqual(profile.role, 'recruteur')

    def test_update_with_files(self):
        mock_picture = SimpleUploadedFile("avatar.jpg", b"fake-image-data", content_type="image/jpeg")
        mock_record = SimpleUploadedFile("casier.pdf", b"fake-pdf-data", content_type="application/pdf")

        data = {
            'full_name': 'Louis Lemoine',
        }

        files = {
            'profile_picture': mock_picture,
            'judicial_record': mock_record,
        }

        profile = update_user_profile(self.user, data, files)

        self.assertTrue(profile.profile_picture)
        self.assertTrue(profile.judicial_record)
