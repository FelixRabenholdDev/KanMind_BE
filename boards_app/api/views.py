from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Q

from boards_app.models import Board
from .serializers import BoardListSerializer, BoardDetailSerializer, BoardCreateSerializer

class BoardViewSet(ModelViewSet):

    def get_serializer_class(self):
        if self.action == "create":
            return BoardCreateSerializer
        if self.action == "retrieve":
            return BoardDetailSerializer
        return BoardListSerializer

    def get_queryset(self):
        return Board.objects.filter(
            Q(owner=self.request.user) |
            Q(members=self.request.user)
        ).distinct().annotate(
            member_count=Count("members", distinct=True),
            ticket_count=Count("tasks", distinct=True),
            tasks_to_do_count=Count(
                "tasks",
                filter=Q(tasks__status="to-do"),
                distinct=True
            ),
            tasks_high_prio_count=Count(
                "tasks",
                filter=Q(tasks__priority="high"),
                distinct=True
            ),
        )

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