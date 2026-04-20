from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated

from .serializers import RegistrationSerializer, LoginSerializer
from boards_app.api.serializers import UserMiniSerializer

User = get_user_model()

class EmailCheckView(APIView):

    def get(self, request):
        email = request.query_params.get("email")

        if not email:
            return Response(
                {"detail": "Email is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"detail": "Email not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            UserMiniSerializer(user).data,
            status=status.HTTP_200_OK
        )
    
class LoginView(GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = self.get_serializer(data=request.data)

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
                }, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception:
            return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RegistrationView(GenericAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        try:    
            serializer = self.get_serializer(data=request.data)

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
        
        except Exception:
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )