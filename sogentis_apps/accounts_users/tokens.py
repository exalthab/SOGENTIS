# accounts_users/tokens.py
from __future__ import annotations

from django.contrib.auth.tokens import PasswordResetTokenGenerator


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """
    Token d’activation (email):
    - devient invalide après activation (car inclut is_active)
    - devient invalide si password change
    - devient invalide si last_login change (optionnel mais ok)
    """

    def _make_hash_value(self, user, timestamp) -> str:
        last_login = getattr(user, "last_login", None)
        last_login_str = "" if last_login is None else last_login.replace(microsecond=0).isoformat()
        return f"{user.pk}{user.password}{timestamp}{user.is_active}{last_login_str}"


account_activation_token = AccountActivationTokenGenerator()





# # accounts_users/tokens.py
# from django.contrib.auth.tokens import PasswordResetTokenGenerator
# from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
# from django.utils.crypto import salted_hmac
# from django.utils.encoding import force_str
# from django.utils import timezone

# class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
#     """
#     Générateur de token d'activation amélioré :
#     - Invalide si mot de passe changé
#     - Invalide si utilisateur désactivé
#     - Permet de vérifier la dernière connexion
#     """
#     def _make_hash_value(self, user, timestamp):
#         login_timestamp = '' if user.last_login is None else user.last_login.replace(microsecond=0, tzinfo=None)
#         return f"{user.pk}{user.password}{timestamp}{user.is_active}{login_timestamp}"

#     def make_token(self, user):
#         """
#         Génère un token unique.
#         """
#         return super().make_token(user)

#     def check_token(self, user, token):
#         """
#         Vérifie si le token est toujours valide.
#         """
#         return super().check_token(user, token)

# account_activation_token = AccountActivationTokenGenerator()
