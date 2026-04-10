from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.BoardListView),
    path('<int:pk>/', views.BoardDetailView),
]