"""
Custom permission classes for board and task access control.

This module defines object-level and request-level permissions
to enforce access rules for boards and tasks, including ownership,
membership, and superuser privileges.
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsBoardOwnerOrMemberOrSuperuser(BasePermission):
    """
    Permission to allow access based on board ownership, membership, or superuser status.

    - Superusers have full access.
    - Owners can delete and modify.
    - Members can view and partially modify (PATCH/Safe methods).
    """

    def has_permission(self, request, view):
        """
        Check if the user is authenticated.

        Args:
            request (Request): Incoming request.
            view (View): View being accessed.

        Returns:
            bool: True if user is authenticated, otherwise False.
        """
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Check object-level permissions for a board.

        Args:
            request (Request): Incoming request.
            view (View): View being accessed.
            obj (Board): Board instance.

        Returns:
            bool: True if access is allowed, otherwise False.
        """
        user = request.user

        if user.is_superuser:
            return True

        if request.method == "DELETE":
            return obj.owner_id == user.id

        if request.method in SAFE_METHODS or request.method == "PATCH":
            return (
                obj.owner_id == user.id
                or obj.members.filter(id=user.id).exists()
            )

        return False
    
class IsBoardMemberForTask(BasePermission):
    """
    Permission to allow access to tasks based on board membership or ownership.

    - Superusers have full access.
    - Board owners and members can access tasks.
    """

    def has_permission(self, request, view):
        """
        Check if the user is authenticated.

        Args:
            request (Request): Incoming request.
            view (View): View being accessed.

        Returns:
            bool: True if authenticated, otherwise False.
        """
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Check object-level permissions for a task via its board.

        Args:
            request (Request): Incoming request.
            view (View): View being accessed.
            obj (Task): Task instance.

        Returns:
            bool: True if access is allowed, otherwise False.
        """
        
        user = request.user
        board = obj.board

        if user.is_superuser:
            return True

        return (
            board.owner_id == user.id
            or board.members.filter(id=user.id).exists()
        )