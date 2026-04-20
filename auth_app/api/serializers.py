"""
Serializers for user authentication and registration.

This module defines serializers used for registering new users
and handling login data validation.
"""
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    Handles creation of new users and validates that both password
    fields match before user creation.
    """

    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        """
        Metadata options for RegistrationSerializer.
        """
        model = User
        fields = ["fullname", "email", "password", "repeated_password"]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def validate(self, data):
        """
        Validate that password and repeated_password match.

        Args:
            data (dict): Incoming validated data.

        Returns:
            dict: Validated data if passwords match.

        Raises:
            serializers.ValidationError: If passwords do not match.
        """
        if data["password"] != data["repeated_password"]:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        """
        Create a new user instance.

        Removes repeated_password from validated data and creates
        a user using Django's create_user method.

        Args:
            validated_data (dict): Cleaned validated data.

        Returns:
            User: Newly created user instance.
        """
        validated_data.pop("repeated_password")

        user = User.objects.create_user(
            username=validated_data["email"],
            email=validated_data["email"],
            password=validated_data["password"],
            fullname=validated_data["fullname"],
        )
        return user
    
class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.

    Validates user credentials (email and password).
    """
    email = serializers.EmailField()
    password = serializers.CharField()