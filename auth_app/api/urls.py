from django.urls import path
from . import views

urlpatterns = [    
    path('login/', views.LoginView.as_view()),
    path('registration/', views.RegistrationView.as_view()),
    path('email-check/', views.email_check, name='email-check'),
]