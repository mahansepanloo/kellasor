from rest_framework import serializers
from .models import User
from .utils import password_validate
import re


READONLYFIELDS = ("id", "date_joined", "last_login")


class UserCreateSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "password", "password2"]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate_username(self, value):
        user = User.objects.filter(username=value).exists()
        if len(value.strip()) <= 2:
            raise serializers.ValidationError(
                "Username must be at least 2 characters long"
            )
        elif user:
            raise serializers.ValidationError("Username already exists")
        return value

    def validate(self, data):
        passwords = data.get("password", None)
        passwords2 = data.get("password2", None)
        password_validate(passwords, passwords2)
        return data

    def create(self, validated_data):
        validated_data.pop("password2")
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
        )
        return user


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
        ]


class UserRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ["password"]
        read_only_fields = READONLYFIELDS


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = READONLYFIELDS + ("username", "first_name", "last_name", "is_active")
        read_only_fields = READONLYFIELDS


class UserUpdateSerializer(AdminUserUpdateSerializer):
    class Meta(AdminUserUpdateSerializer.Meta):
        model = User
        fields = ["username", "first_name", "last_name"]


class ResetPasswordSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)
    old_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = "__all__"
        exclude = ["password"]

    def validate(self, data):
        passwords = data["password"]
        passwords2 = data["password2"]
        old = data["old_password"]
        user = self.context["request"].user
        if user.check_password(old):
            password_validate(passwords, passwords2)
            return data
        else:
            return serializers.ValidationError("Old password is incorrect")


class ForgetPasswordSerializer(serializers.Serializer):
    username = serializers.CharField()
    phone = serializers.CharField()

    def validate_phone(self, value):
        patterns = [
            re.compile(r"^\+98\d{10}$"),
            re.compile(r"^09\d{9}$"),
        ]
        if not any(p.match(value) for p in patterns):
            raise serializers.ValidationError("Phone number is not valid")
        return value


class VerifyCodeSerializer(serializers.Serializer):
    phone = serializers.CharField()
    code = serializers.CharField()
    password = serializers.CharField()
    password2 = serializers.CharField()

    def validate(self, data):
        passwords = data["password"]
        passwords2 = data["password2"]
        password_validate(passwords, passwords2)
        return data
