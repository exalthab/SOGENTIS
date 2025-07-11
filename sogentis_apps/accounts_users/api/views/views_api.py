from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class UserDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile = user.userprofile
        return Response({
            'email': user.email,
            'full_name': profile.full_name,
            'role': profile.role.name if profile.role else None,
            'country': profile.country,
            'phone': profile.phone,
        })
