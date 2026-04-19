from rest_framework import serializers
from boards_app.models import Board, Task, User

class BoardListSerializer(serializers.ModelSerializer):
    member_count = serializers.IntegerField(read_only=True)
    ticket_count = serializers.IntegerField(read_only=True)
    tasks_to_do_count = serializers.IntegerField(read_only=True)
    tasks_high_prio_count = serializers.IntegerField(read_only=True)
    owner_id = serializers.IntegerField(source="owner.id", read_only=True)

    class Meta:
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
    class Meta:
        model = User
        fields = ["id", "email", "fullname"]

class BoardTaskSerializer(serializers.ModelSerializer):
    assignee = UserMiniSerializer(read_only=True)
    reviewer = UserMiniSerializer(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
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
    owner_id = serializers.IntegerField(source="owner.id", read_only=True)

    members = UserMiniSerializer(many=True, read_only=True)
    tasks = BoardTaskSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "owner_id",
            "members",
            "tasks",
        ]

class BoardCreateSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), write_only=True)

    class Meta:
        model = Board
        fields = ["title", "members"]

    def create(self, validated_data):
        members = validated_data.pop("members", [])
        request = self.context["request"]

        board = Board.objects.create(
            title=validated_data["title"],
            owner=request.user
        )

        board.members.set([request.user, *members])

        return board
    
class TaskCreateSerializer(serializers.ModelSerializer):
    assignee_id = serializers.IntegerField(required=False, allow_null=True)
    reviewer_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
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
        request = self.context["request"]
        user = request.user

        board = data["board"]

        if not (board.owner == user or board.members.filter(id=user.id).exists()):
            raise serializers.ValidationError("Not a member of this board.")

        if data["status"] not in ["to-do", "in-progress", "review", "done"]:
            raise serializers.ValidationError("Invalid status.")

        if data["priority"] not in ["low", "medium", "high"]:
            raise serializers.ValidationError("Invalid priority.")

        return data

    def create(self, validated_data):
        assignee_id = validated_data.pop("assignee_id", None)
        reviewer_id = validated_data.pop("reviewer_id", None)

        board = validated_data["board"]

        assignee = None
        reviewer = None

        if assignee_id:
            assignee = User.objects.filter(id=assignee_id).first()
            if not board.members.filter(id=assignee_id).exists():
                raise serializers.ValidationError("Assignee must be board member.")

        if reviewer_id:
            reviewer = User.objects.filter(id=reviewer_id).first()
            if not board.members.filter(id=reviewer_id).exists():
                raise serializers.ValidationError("Reviewer must be board member.")

        task = Task.objects.create(
            assignee=assignee,
            reviewer=reviewer,
            **validated_data
        )

        return task
    
class TaskSerializer(serializers.ModelSerializer):
    assignee = serializers.SerializerMethodField()
    reviewer = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
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
        if not obj.assignee:
            return None
        return {
            "id": obj.assignee.id,
            "email": obj.assignee.email,
            "fullname": obj.assignee.fullname,
        }

    def get_reviewer(self, obj):
        if not obj.reviewer:
            return None
        return {
            "id": obj.reviewer.id,
            "email": obj.reviewer.email,
            "fullname": obj.reviewer.fullname,
        }

    def get_comments_count(self, obj):
        return obj.comments.count()