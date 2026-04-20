"""
URL routing for task-related API endpoints.

This module defines endpoints for creating tasks, filtering tasks,
retrieving task details, and managing task comments.
"""

from django.urls import path
from .views import TaskCreateView, TaskFilteredView, TaskDetailView, TaskCommentsView, TaskCommentDeleteView

urlpatterns = [
    path("", TaskCreateView.as_view()),
    path("reviewing/", TaskFilteredView.as_view()),
    path("assigned-to-me/", TaskFilteredView.as_view()),
    path("<int:task_id>/", TaskDetailView.as_view()),
    path("<int:task_id>/comments/", TaskCommentsView.as_view()), 
    path("<int:task_id>/comments/<int:comment_id>/", TaskCommentDeleteView.as_view()),
]