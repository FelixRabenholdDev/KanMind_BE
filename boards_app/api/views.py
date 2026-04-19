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

    permission_classes = [IsBoardOwnerOrMemberOrSuperuser]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_serializer_class(self):
        if self.action == "create":
            return BoardCreateSerializer
        if self.action == "retrieve":
            return BoardDetailSerializer
        if self.action == "partial_update":
            return BoardCreateSerializer
        return BoardListSerializer
    
    def get_annotated_queryset(self, qs):
        return qs.annotate(
            member_count=Count("members", distinct=True),
            ticket_count=Count("tasks", distinct=True),
            tasks_to_do_count=Count("tasks", filter=Q(tasks__status="to-do"), distinct=True),
            tasks_high_prio_count=Count("tasks", filter=Q(tasks__priority="high"), distinct=True),
        )
    
    def get_queryset(self):
        user = self.request.user
        qs = Board.objects.all()

        if not user.is_superuser:
            qs = qs.filter(
                Q(owner=user) | Q(members=user)
            ).distinct()

        if self.action == "list":
            qs = self.get_annotated_queryset(qs)

        return qs
    
    def perform_create(self, serializer):
        board = serializer.save(owner=self.request.user)
        board.members.add(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        board = serializer.save(owner=request.user)
        board.members.add(request.user)

        board = self.get_queryset().get(pk=board.pk)

        output = BoardListSerializer(board, context={"request": request})

        return Response(output.data, status=status.HTTP_201_CREATED)
    
    def partial_update(self, request, *args, **kwargs):
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
    def get(self, request):
        user = request.user
        f = request.query_params.get("filter")

        qs = Task.objects.all()

        if f == "assigned":
            qs = qs.filter(assignee=user)
        elif f == "reviewing":
            qs = qs.filter(reviewer=user)

        serializer = TaskSerializer(qs, many=True)
        return Response(serializer.data)

class TaskCreateView(APIView):

    def post(self, request):
        serializer = TaskCreateSerializer(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        task = serializer.save()

        output = TaskSerializer(task)

        return Response(output.data, status=status.HTTP_201_CREATED)
    
class TaskDetailView(APIView):
    permission_classes = [IsBoardMemberForTask]

    def get_object(self, task_id):
        return get_object_or_404(
            Task.objects.select_related("board", "assignee", "reviewer"),
            id=task_id
        )

    def patch(self, request, task_id):
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