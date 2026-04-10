from django.urls import path
from . import views

urlpatterns = [
    path('', views.TaskListView),
    path('<int:pk/>', views.TaskDetailView),
]