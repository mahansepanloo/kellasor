from rest_framework import serializers
from accounts_app.models import User
from .models import ClassRooms, Students
from rest_framework.exceptions import ValidationError
from accounts_app.Serializer import UserSerializerList


class ClassRoomCreatedSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassRooms
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at", "teacher", "created_by"]

    def validate(self, attrs):
        if attrs["class_type"] == "private" and (
            not attrs["access_type"] or attrs["access_type"] == ""
        ):
            raise ValidationError("Password is required")
        return attrs


class ClassRoomEditSerializer(serializers.ModelSerializer):
    mentor = UserSerializerList(many=True, required=False)
    teacher = UserSerializerList(many=True, required=False)

    class Meta:
        model = ClassRooms
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at", "created_by"]


class ClassRoomListSerializer(serializers.ModelSerializer):
    teacher = UserSerializerList(many=True, required=False)

    class Meta:
        model = ClassRooms
        fields = ["name", "class_type", "capacity", "access_type", "teacher"]
        read_only_fields = ["id", "created_at", "updated_at", "created_by"]


class PasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255)

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Students
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at", "created_by"]