from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.BoardListView),
    path('<int:board_id>/', views.BoardDetailView),
    path('<int:board_id>/tasks/', include('tasks_app.urls')),
]