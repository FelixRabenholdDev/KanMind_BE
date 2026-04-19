from django.db.models import Count, Q

from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status

from boards_app.models import Board
from .serializers import BoardListSerializer, BoardDetailSerializer, BoardCreateSerializer
from .permissions import IsBoardOwnerOrMemberOrSuperuser

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