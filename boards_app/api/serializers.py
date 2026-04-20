"""
Serializers for boards and tasks.

This module defines serializers used for:
- board listing and detail views
- board creation
- task creation and representation
- lightweight user representation
"""

from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, NotFound
from boards_app.models import Board, Task, User

class BoardListSerializer(serializers.ModelSerializer):
    """
    Serializer for board list view.

    Provides aggregated board statistics such as member count
    and task-related metrics.
    """

    member_count = serializers.IntegerField(read_only=True)
    ticket_count = serializers.IntegerField(read_only=True)
    tasks_to_do_count = serializers.IntegerField(read_only=True)
    tasks_high_prio_count = serializers.IntegerField(read_only=True)
    owner_id = serializers.IntegerField(source="owner.id", read_only=True)

    class Meta:
        """
        Meta options for BoardListSerializer.
        """

        model = Board
        fields = [
            "id",
            "title",            
            "member_count",
            "ticket_count",
            "tasks_to_do_count",
            "tasks_high_prio_count",
            "owner_id",
        ]

class UserMiniSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for user representation.

    Used in nested relations where only basic user information is required.
    """

    class Meta:
        """
        Meta options for UserMiniSerializer.
        """

        model = User
        fields = ["id", "email", "fullname"]

class BoardTaskSerializer(serializers.ModelSerializer):
    """
    Serializer for tasks inside board detail view.

    Includes nested assignee/reviewer information and comment count.
    """

    assignee = UserMiniSerializer(read_only=True)
    reviewer = UserMiniSerializer(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        """
        Meta options for BoardTaskSerializer.
        """

        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "reviewer",
            "due_date",
            "comments_count",
        ]

class BoardDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed board view.

    Includes members and all related tasks.
    """

    owner_id = serializers.IntegerField(source="owner.id", read_only=True)

    members = UserMiniSerializer(many=True, read_only=True)
    tasks = BoardTaskSerializer(many=True, read_only=True)

    class Meta:
        """
        Meta options for BoardDetailSerializer.
        """

        model = Board
        fields = [
            "id",
            "title",
            "owner_id",
            "members",
            "tasks",
        ]

class BoardCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating boards.

    Automatically assigns the requesting user as owner and member.
    """

    members = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), write_only=True)

    class Meta:
        """
        Meta options for BoardCreateSerializer.
        """

        model = Board
        fields = ["title", "members"]

    def create(self, validated_data):
        """
        Create a new board and assign members.

        Args:
            validated_data (dict): Validated input data.

        Returns:
            Board: Newly created board instance.
        """

        members = validated_data.pop("members", [])
        request = self.context["request"]

        board = Board.objects.create(
            title=validated_data["title"],
            owner=request.user
        )

        board.members.set([request.user, *members])

        return board
    
class TaskCreateSerializer(serializers.ModelSerializer):
    """
    Serialize task creation requests.

    Validates board membership and ensures assignee/reviewer
    are valid board members.
    """

    assignee_id = serializers.IntegerField(required=False, allow_null=True)
    reviewer_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        """
        Meta options for TaskCreateSerializer.
        """

        model = Task
        fields = [
            "board",
            "title",
            "description",
            "status",
            "priority",
            "assignee_id",
            "reviewer_id",
            "due_date",
        ]

    def validate(self, data):
        """
        Validate task creation constraints.

        Ensures:
        - user is member of board
        - status and priority values are valid

        Args:
            data (dict): Incoming validated or partially validated task data.

        Returns:
            dict: The validated task data.

        Raises:
            serializers.ValidationError: If validation fails.
        """

        request = self.context["request"]
        user = request.user

        board = data["board"]

        if not board:
            raise NotFound("Board not found.")

        if not (board.owner == user or board.members.filter(id=user.id).exists()):
            raise PermissionDenied("Not a member of this board.")

        if data["status"] not in ["to-do", "in-progress", "review", "done"]:
            raise serializers.ValidationError("Invalid status.")

        if data["priority"] not in ["low", "medium", "high"]:
            raise serializers.ValidationError("Invalid priority.")

        return data

    def create(self, validated_data):
        """
        Create a new task instance.

        Ensures assignee and reviewer are valid board members.

        Args:
            validated_data (dict): Cleaned input data.

        Returns:
            Task: Created task instance.
        """

        assignee_id = validated_data.pop("assignee_id", None)
        reviewer_id = validated_data.pop("reviewer_id", None)

        board = validated_data["board"]

        assignee = None
        reviewer = None

        if assignee_id:
            assignee = User.objects.filter(id=assignee_id).first()
            if not board.members.filter(id=assignee_id).exists():
                raise PermissionDenied("Assignee must be board member.")

        if reviewer_id:
            reviewer = User.objects.filter(id=reviewer_id).first()
            if not board.members.filter(id=reviewer_id).exists():
                raise PermissionDenied("Reviewer must be board member.")

        task = Task.objects.create(
            assignee=assignee,
            reviewer=reviewer,
            **validated_data
        )

        return task
    
class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for task detail representation.

    Provides nested user information and computed comment count.
    """

    assignee = serializers.SerializerMethodField()
    reviewer = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        """
        Meta options for TaskSerializer.
        """

        model = Task
        fields = [
            "id",
            "board",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "reviewer",
            "due_date",
            "comments_count",
        ]

    def get_assignee(self, obj):
        """
        Return serialized assignee data.

        Args:
            obj (Task): Task instance.

        Returns:
            dict | None: Assignee data or None.
        """

        if not obj.assignee:
            return None
        return {
            "id": obj.assignee.id,
            "email": obj.assignee.email,
            "fullname": obj.assignee.fullname,
        }

    def get_reviewer(self, obj):
        """
        Return serialized reviewer data.

        Args:
            obj (Task): Task instance.

        Returns:
            dict | None: Reviewer data or None.
        """

        if not obj.reviewer:
            return None
        return {
            "id": obj.reviewer.id,
            "email": obj.reviewer.email,
            "fullname": obj.reviewer.fullname,
        }

    def get_comments_count(self, obj):
        """
        Return number of comments for the task.

        Args:
            obj (Task): Task instance.

        Returns:
            int: Number of related comments.
        """
        
        return obj.comments.count()