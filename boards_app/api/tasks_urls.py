from django.urls import path
from .views import TaskCreateView, TaskFilteredView, TaskDetailView

urlpatterns = [
    path("", TaskCreateView.as_view()),
    path("reviewing/", TaskFilteredView.as_view()),
    path("assigned-to-me/", TaskFilteredView.as_view()),
    path("<int:task_id>/", TaskDetailView.as_view()),
]