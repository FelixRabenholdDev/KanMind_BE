from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from .serializers import RegistrationSerializer, LoginSerializer

User = get_user_model()

class EmailCheckView(GenericAPIView):
    def get(self, request):
        try:
            if not request.user or not request.user.is_authenticated:
                return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
            
            email = request.query_params.get("email")
        
            if not email:
                return Response({"error": "Email parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                validate_email(email)
            except ValidationError:
                return Response({"error": "Invalid email format"}, status=status.HTTP_400_BAD_REQUEST)
            
            user = User.objects.filter(email=email).first()
            if not user:
                return Response({"error": "Email not found"}, status=status.HTTP_404_NOT_FOUND)

            return Response({
                "id": user.id,
                "email": user.email,
                "fullname": user.fullname
            }, status=status.HTTP_200_OK)
        
        except Exception:
            return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
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