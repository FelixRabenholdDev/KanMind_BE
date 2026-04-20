"""
URL configuration for authentication endpoints.

This module defines the URL routes for user authentication,
including registration and login views.
"""

from django.urls import path

from .views import RegistrationView, LoginView

urlpatterns = [    
    path('login/', LoginView.as_view(), name='login'),
    path('registration/', RegistrationView.as_view(), name='registration'),
]