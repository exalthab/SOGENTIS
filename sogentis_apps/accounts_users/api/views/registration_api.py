from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from accounts_users.forms.signup_forms import UserSignupForm 
from accounts_users.forms.profile_forms import UserProfileForm

class RegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data.copy()
        files = request.FILES

        # Création des formulaires
        user_form = UserSignupForm(data)
        profile_form = UserProfileForm(data, files)

        if user_form.is_valid() and profile_form.is_valid():
            # Création de l'utilisateur
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data["password"])
            user.save()

            # Création du profil utilisateur
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            return Response({'detail': 'Inscription réussie.'}, status=status.HTTP_201_CREATED)

        return Response({
            'user_errors': user_form.errors,
            'profile_errors': profile_form.errors
        }, status=status.HTTP_400_BAD_REQUEST)




# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status, permissions
# from accounts_users.forms.signup_forms import UserSignupForm, UserProfileForm

# class RegisterAPIView(APIView):
#     permission_classes = [permissions.AllowAny]

#     def post(self, request):
#         user_form = UserSignupForm(request.data)
#         profile_form = UserProfileForm(request.data)
#         if user_form.is_valid() and profile_form.is_valid():
#             user = user_form.save(commit=False)
#             user.set_password(user_form.cleaned_data["password"])
#             user.save()
#             profile = profile_form.save(commit=False)
#             profile.user = user
#             profile.save()
#             return Response({'detail': 'Inscription réussie.'}, status=status.HTTP_201_CREATED)
#         return Response({
#             'user_errors': user_form.errors,
#             'profile_errors': profile_form.errors
#         }, status=status.HTTP_400_BAD_REQUEST)
