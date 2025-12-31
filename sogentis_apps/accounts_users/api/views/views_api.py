# accounts_users/api/views/views_api.py 21/12/2025

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class UserDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Sécurité : éviter AttributeError si le profil n'existe pas encore
        profile = getattr(user, "userprofile", None)

        if not profile:
            return Response(
                {
                    "email": user.email,
                    "full_name": None,
                    "role": None,
                    "country_of_residence": None,
                    "phone": None,
                }
            )

        full_name = f"{profile.last_name or ''} {profile.first_name or ''}".strip()

        return Response({
            "email": user.email,
            "full_name": full_name or None,
            "role": profile.role.name if profile.role else None,
            "country": profile.country,

            "country_of_residence": (
                profile.country_of_residence
                if profile.country_of_residence
                else None
            ),
            "phone": profile.phone,
        })








# # accounts_users/api/views/views_api.py November 2025
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated

# class UserDetailAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user
#         profile = user.userprofile
#         return Response({
#             'email': user.email,
#             'full_name': profile.full_name,
#             'role': profile.role.name if profile.role else None,
#             # 'country': profile.country,
#             'phone': profile.phone,
#         })




