from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import update_session_auth_hash
from accounts_users.forms.password_forms import CustomPasswordChangeForm

class PasswordResetAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        form = PasswordResetForm(data=request.data)
        if form.is_valid():
            form.save(request=request)
            return Response({'detail': 'Un email de réinitialisation a été envoyé.'})
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        form = CustomPasswordChangeForm(user=request.user, data=request.data)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return Response({'detail': 'Mot de passe changé avec succès.'})
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
