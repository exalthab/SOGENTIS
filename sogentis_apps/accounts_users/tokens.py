# accounts_users/tokens.py
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{timestamp}{user.is_active}"

account_activation_token = AccountActivationTokenGenerator()




## accounts_users/tokens.py - > 01/07/
# from django.contrib.auth.tokens import PasswordResetTokenGenerator

# class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
#     def _make_hash_value(self, user, timestamp):
#         return f"{user.pk}{timestamp}{user.is_active}"

# account_activation_token = AccountActivationTokenGenerator()
