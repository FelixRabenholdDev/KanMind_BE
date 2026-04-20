"""
API views for boards, tasks, and comments.

This module contains view logic for:
- board management (CRUD with annotations and membership rules)
- task filtering, creation, and detail operations
- comment creation and deletion on tasks
"""

from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from boards_app.models import Board, Task, Comment
from .serializers import BoardListSerializer, BoardDetailSerializer, BoardCreateSerializer, TaskCreateSerializer, TaskSerializer
from .permissions import IsBoardOwnerOrMemberOrSuperuser, IsBoardMemberForTask

User = get_user_model()

class BoardViewSet(ModelViewSet):
    """
    ViewSet for managing boards.

    Supports listing, retrieving, creating, updating, and deleting boards
    with annotation-based statistics and permission checks.
    """

    permission_classes = [IsBoardOwnerOrMemberOrSuperuser]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_serializer_class(self):
        """
        Return appropriate serializer based on action.

        Returns:
            Serializer class
        """
        if self.action == "create":
            return BoardCreateSerializer
        if self.action == "retrieve":
            return BoardDetailSerializer
        if self.action == "partial_update":
            return BoardCreateSerializer
        return BoardListSerializer
    
    def get_annotated_queryset(self, qs):
        """
        Annotate queryset with board statistics.

        Args:
            qs (QuerySet): Base queryset

        Returns:
            QuerySet: Annotated queryset
        """
        return qs.annotate(
            member_count=Count("members", distinct=True),
            ticket_count=Count("tasks", distinct=True),
            tasks_to_do_count=Count("tasks", filter=Q(tasks__status="to-do"), distinct=True),
            tasks_high_prio_count=Count("tasks", filter=Q(tasks__priority="high"), distinct=True),
        )
    
    def get_queryset(self):
        """
        Return filtered queryset depending on user and action.

        Returns:
            QuerySet: Boards accessible to the user
        """
        user = self.request.user
        qs = Board.objects.all()

        if self.action == "list" and not user.is_superuser:
            qs = qs.filter(
                Q(owner=user) | Q(members=user)
            ).distinct()

        if self.action == "list":
            qs = self.get_annotated_queryset(qs)

        return qs
    
    def create(self, request, *args, **kwargs):
        """
        Create a new board.

        Returns:
            Response: Created board data
        """
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        board = serializer.save()

        board = self.get_annotated_queryset(Board.objects.filter(pk=board.pk)).first()

        output = {
        "id": board.id,
        "title": board.title,
        "member_count": board.member_count,
        "ticket_count": board.ticket_count,
        "tasks_to_do_count": board.tasks_to_do_count,
        "tasks_high_prio_count": board.tasks_high_prio_count,
        "owner_id": board.owner_id,
        }

        return Response(output, status=status.HTTP_201_CREATED)
    
    def partial_update(self, request, *args, **kwargs):
        """
        Partially update a board.

        Returns:
            Response: Updated board data
        """
        board = self.get_object()

        serializer = self.get_serializer(board, data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)

        if "title" in serializer.validated_data:
            board.title = serializer.validated_data["title"]

        if "members" in serializer.validated_data:
            board.members.set(serializer.validated_data["members"])

        board.save()

        output = {
            "id": board.id,
            "title": board.title,
            "owner_data": {
                "id": board.owner.id,
                "email": board.owner.email,
                "fullname": board.owner.fullname
            },
            "members_data": [
                {
                    "id": m.id,
                    "email": m.email,
                    "fullname": m.fullname
                }
                for m in board.members.all()
            ]
        }

        return Response(output, status=status.HTTP_200_OK)

class TaskFilteredView(APIView):
    """
    API view for filtering tasks based on user role (assignee/reviewer).
    """

    def get(self, request):
        """
        Return tasks filtered by request path.

        Returns:
            Response: List of serialized tasks
        """
        user = request.user
        qs = Task.objects.all()

        if "assigned" in request.path:
            qs = qs.filter(assignee=user)
        elif "reviewing" in request.path:
            qs = qs.filter(reviewer=user)

        serializer = TaskSerializer(qs, many=True)
        return Response(serializer.data)

class TaskCreateView(APIView):
    """
    API view for creating tasks.
    """

    def post(self, request):
        """
        Create a new task.

        Returns:
            Response: Created task data
        """
        serializer = TaskCreateSerializer(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        task = serializer.save()

        output = TaskSerializer(task)

        return Response(output.data, status=status.HTTP_201_CREATED)
    
class TaskDetailView(APIView):
    """
    API view for retrieving, updating, and deleting a task.
    """

    permission_classes = [IsBoardMemberForTask]

    def get_object(self, task_id):
        """
        Retrieve a task instance.

        Args:
            task_id (int): Task ID

        Returns:
            Task: Task instance
        """
        return get_object_or_404(
            Task.objects.select_related("board", "assignee", "reviewer"),
            id=task_id
        )

    def patch(self, request, task_id):
        """
        Partially update a task.

        Returns:
            Response: Updated task data
        """
        task = self.get_object(task_id)

        self.check_object_permissions(request, task)

        data = request.data

        if "board" in data:
            return Response(
                {"error": "Changing board is not allowed"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if "status" in data and data["status"] not in ["to-do", "in-progress", "review", "done"]:
            return Response(
                {"error": "Invalid status"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if "priority" in data and data["priority"] not in ["low", "medium", "high"]:
            return Response(
                {"error": "Invalid priority"},
                status=status.HTTP_400_BAD_REQUEST
            )

        for field in ["title", "description", "status", "priority", "due_date"]:
            if field in data:
                setattr(task, field, data[field])

        if "assignee_id" in data:
            assignee = User.objects.filter(id=data["assignee_id"]).first()

            if assignee and not task.board.members.filter(id=assignee.id).exists():
                return Response(
                    {"error": "Assignee must be board member"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            task.assignee = assignee

        if "reviewer_id" in data:
            reviewer = User.objects.filter(id=data["reviewer_id"]).first()

            if reviewer and not task.board.members.filter(id=reviewer.id).exists():
                return Response(
                    {"error": "Reviewer must be board member"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            task.reviewer = reviewer

        task.save()

        return Response(TaskSerializer(task).data, status=status.HTTP_200_OK)

    def delete(self, request, task_id):
        """
        Delete a task (only allowed for board owner).

        Returns:
            Response: Empty response on success
        """
        if not str(task_id).isdigit():
            return Response(
                {"error": "Invalid task id"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        task = self.get_object(task_id)

        self.check_object_permissions(request, task)

        if task.board.owner != request.user:
            return Response(
                {"error": "Only board owner can delete tasks"},
                status=status.HTTP_403_FORBIDDEN
            )

        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class TaskCommentsView(APIView):
    """
    API view for listing and creating comments on a task.
    """
    permission_classes = [IsBoardMemberForTask]

    def get_task(self, task_id):
        """
        Retrieve task instance.

        Returns:
            Task
        """
        return get_object_or_404(Task, id=task_id)

    def get(self, request, task_id):
        """
        List comments for a task.

        Returns:
            Response: List of comments
        """
        task = self.get_task(task_id)
        self.check_object_permissions(request, task)

        comments = Comment.objects.filter(task=task).order_by("created_at")

        return Response([
            {
                "id": c.id,
                "created_at": c.created_at,
                "author": c.author.fullname,
                "content": c.content
            }
            for c in comments
        ])

    def post(self, request, task_id):
        """
        Create a comment on a task.

        Returns:
            Response: Created comment data
        """
        task = self.get_task(task_id)
        self.check_object_permissions(request, task)

        content = request.data.get("content", "").strip()

        if not content:
            return Response({"error": "Content required"}, status=400)

        comment = Comment.objects.create(
            task=task,
            author=request.user,
            content=content
        )

        return Response({
            "id": comment.id,
            "created_at": comment.created_at,
            "author": request.user.fullname,
            "content": comment.content
        }, status=201)
    
class TaskCommentDeleteView(APIView):
    """
    API view for deleting comments from a task.
    """
    permission_classes = [IsBoardMemberForTask]

    def get_task(self, task_id):
        """
        Retrieve task instance.
        """
        return get_object_or_404(Task, id=task_id)

    def get_comment(self, task, comment_id):
        """
        Retrieve comment instance.

        Returns:
            Comment
        """
        return get_object_or_404(
            Comment,
            id=comment_id,
            task=task
        )

    def delete(self, request, task_id, comment_id):
        """
        Delete a comment.

        Returns:
            Response: Empty response on success
        """
        task = self.get_task(task_id)

        self.check_object_permissions(request, task)

        comment = self.get_comment(task, comment_id)

        if request.user.is_superuser:
            return True

        if comment.author != request.user:
            return Response(
                {"error": "Only comment author or admin can delete this comment"},
                status=status.HTTP_403_FORBIDDEN
            )

        comment.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)