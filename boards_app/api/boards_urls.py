"""
URL routing for board-related API endpoints.

This module defines the router configuration for the BoardViewSet,
which handles CRUD operations for boards.
"""

from rest_framework.routers import DefaultRouter

from .views import BoardViewSet

router = DefaultRouter()
router.register(r"", BoardViewSet, basename="boards")

urlpatterns = router.urls