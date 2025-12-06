from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model
from accounts_users.tokens import account_activation_token

User = get_user_model()

class ActivateAccountView(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"detail": "Lien invalide."}, status=status.HTTP_400_BAD_REQUEST)

        if account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({"detail": "Compte activé avec succès."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Lien d’activation invalide ou expiré."}, status=status.HTTP_400_BAD_REQUEST)
