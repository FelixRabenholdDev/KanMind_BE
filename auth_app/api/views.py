from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailCheckView(APIView):
    def get(self, request):
        email = request.query_params.get("email")
        user = User.objects.filter(email=email).first()

        if not user:
            return Response({}, status=404)

        return Response({
            "id": user.id,
            "email": user.email,
            "fullname": user.fullname
        })
    
class LoginView(APIView):
    pass

class RegistrationView(APIView):
    pass