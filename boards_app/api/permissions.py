from rest_framework.permissions import BasePermission

class IsBoardOwnerOrMemberOrSuperuser(BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.is_superuser:
            return True

        if request.method == "DELETE":
            return obj.owner_id == user.id

        if request.method in ["GET", "PATCH"]:
            return (
                obj.owner_id == user.id
                or obj.members.filter(id=user.id).exists()
            )

        return False
    
class IsBoardMemberForTask(BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        board = obj.board

        if user.is_superuser:
            return True

        return (
            board.owner_id == user.id
            or board.members.filter(id=user.id).exists()
        )