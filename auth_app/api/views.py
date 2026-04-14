from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

from .serializers import RegistrationSerializer, LoginSerializer

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
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"error": "Invalid credentials"}, status=400)

            if not user.check_password(password):
                return Response({"error": "Invalid credentials"}, status=400)

            token, _ = Token.objects.get_or_create(user=user)

            return Response({
                "token": token.key,
                "fullname": user.fullname,
                "email": user.email,
                "user_id": user.id
            })

        return Response(serializer.errors, status=400)

class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            token, _ = Token.objects.get_or_create(user=user)

            return Response({
                "token": token.key,
                "fullname": user.fullname,
                "email": user.email,
                "user_id": user.id
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)