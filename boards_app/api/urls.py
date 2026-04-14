from django.urls import path
from . import views

urlpatterns = [
    path('', views.BoardListView.as_view()),
    path('<int:pk>/', views.BoardDetailView.as_view()),
]