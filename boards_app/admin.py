"""
Admin configuration for User, Board, and Task models.

This module customizes the Django admin interface for:
- CustomUserAdmin: extends Django's default UserAdmin
- BoardAdmin: manages boards and their related tasks
- TaskAdmin: manages individual tasks
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Board, Task


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Admin configuration for the custom User model.

    Extends the default Django UserAdmin by adding custom fields
    such as 'fullname' and adjusting list display and search options.
    """

    model = User
    fieldsets = UserAdmin.fieldsets + (
        ("Custom Fields", {"fields": ("fullname",)}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Custom Fields", {
            "classes": ("wide",),
            "fields": ("email", "username", "fullname", "password1", "password2"),
        }),
    )

    list_display = ("email", "username", "fullname", "is_staff", "is_superuser", "is_active")
    list_filter = ("is_staff", "is_superuser", "is_active")

    search_fields = ("email", "username", "fullname")
    ordering = ("email",)

    readonly_fields = ()

class TaskInline(admin.TabularInline):
    """
    Inline admin interface for Task objects inside Board admin.

    Allows tasks to be created and edited directly within a Board.
    """
    model = Task
    extra = 1

@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    """
    Admin configuration for Board model.

    Displays boards with their owner and allows inline editing
    of related Task objects.
    """

    list_display = ("title", "owner")
    search_fields = ("title",)
    inlines = [TaskInline]

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """
    Admin configuration for Task model.

    Provides filtering and search capabilities for tasks
    across boards and completion status.
    """

    list_display = ("title", "board", "status")
    list_filter = ("status", "board")
    search_fields = ("title", "description")