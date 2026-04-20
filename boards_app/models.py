"""
Database models for users, boards, tasks, and comments.

This module defines the core data structure of the application,
including a custom user model, board collaboration system,
task management, and commenting functionality.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.

    Uses email as the unique identifier instead of username.
    """

    fullname = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

class Board(models.Model):
    """
    Represents a collaborative board.

    A board can have an owner and multiple members.
    """

    title = models.CharField(max_length=255)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owner_boards')

    members = models.ManyToManyField(settings.AUTH_USER_MODEL, through="BoardMember", related_name="boards")

    created_at = models.DateTimeField(auto_now_add=True)

class BoardMember(models.Model):
    """
    Intermediate model representing membership of users in boards.

    Ensures a user can only be added once per board.
    """

    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        """
        Meta options for BoardMember.
        """

        unique_together = ('board', 'user')

class Task(models.Model):
    """
    Task entity belonging to a board.

    Supports status tracking, priority levels, assignment,
    and review workflow.
    """

    class Status(models.TextChoices):
        """Possible states of a task."""

        TODO = "to-do"
        IN_PROGRESS = "in-progress"
        REVIEW = "review"
        DONE = "done"

    class Priority(models.TextChoices):
        """Priority levels for a task."""

        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"

    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="tasks")

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TODO)

    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)

    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_tasks")

    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="review_tasks")

    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    """
    Comment attached to a task.

    Represents user-generated discussion entries on tasks.
    """
    
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)