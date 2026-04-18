from django.db.models import Count, Q

from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status

from boards_app.models import Board
from .serializers import BoardListSerializer, BoardDetailSerializer, BoardCreateSerializer

class BoardViewSet(ModelViewSet):

    def get_serializer_class(self):
        if self.action == "create":
            return BoardCreateSerializer
        if self.action == "retrieve":
            return BoardDetailSerializer
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

        if user.is_superuser:
            return self.get_annotated_queryset(qs)

        qs = qs.filter(
            Q(owner=user) | Q(members=user)
        ).distinct()

        return self.get_annotated_queryset(qs)

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