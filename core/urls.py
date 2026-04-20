"""
Project URL configuration.

This module defines the global URL routing for the application,
including admin routes, authentication endpoints, and API modules
for boards, tasks, and user-related utilities.
"""
from django.contrib import admin
from django.urls import path, include
from auth_app.api.views import EmailCheckView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/', include('auth_app.api.urls')),
    path('api/boards/', include('boards_app.api.boards_urls')),
    path('api/tasks/', include('boards_app.api.tasks_urls')),
    path('api/email-check/', EmailCheckView.as_view(), name="email-check"),
]
