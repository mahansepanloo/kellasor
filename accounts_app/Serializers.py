from django.core.cache import cache
from rest_framework import serializers
from .models import User
from .utils import password_validate
from utls.response import ResponseMessage

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
                ResponseMessage.error("Username must be at least 2 characters long")
            )
        elif user:
            raise serializers.ValidationError(
                ResponseMessage.error("Username already exists")
            )
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


class ChangePasswordSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)
    old_password = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["password", "password2", "old_password"]

    def validate(self, data):
        passwords = data.get("password")
        passwords2 = data.get("password2")
        old_password = data.get("old_password")
        user = self.context["request"].user
        if user.check_password(old_password):
            password_validate(passwords, passwords2)
            return data
        else:
            raise serializers.ValidationError(
                ResponseMessage.error("Old password is incorrect")
            )

    def update(self, instance, validated_data):
        instance.set_password(validated_data["password"])
        instance.save(update_fields=["password"])
        return instance


class ForgetPasswordSerializer(serializers.Serializer):
    username = serializers.CharField()

    def validate(self, data):
        self.instance = User.objects.filter(username=data["username"]).first()
        return data


class VerifyCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    code = serializers.CharField()
    password = serializers.CharField()
    password2 = serializers.CharField()

    def validate(self, data):
        cached_data = cache.get(data["phone_number"])
        if not cached_data:
            raise serializers.ValidationError({"error": "code not correct"})

        if str(cached_data["code"]) != data["code"]:
            raise serializers.ValidationError({"error": "code not correct"})

        password_validate(data["password"], data["password2"])

        self.instance = User.objects.filter(username=cached_data["username"]).first()

        if not self.instance:
            raise serializers.ValidationError({"error": "user not found"})

        return data

    def change_password(self):
        self.instance.set_password(self.validated_data["password"])
        self.instance.save(update_fields=["password"])
        cache.delete(self.validated_data["phone_number"])
