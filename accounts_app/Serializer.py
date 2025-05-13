from rest_framework import serializers
from .models import User
from .validate import password_format
import re


class UserSerializerList(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name"]
        read_only_fields = ("id", "date_joined", "last_login")


class UserSerializerRetrieve(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ["password"]
        read_only_fields = ("id", "date_joined", "last_login")


class UserSerializerRegister(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "password", "password2"]
        extra_kwargs = {
            "password": {"write_only": True},
        }
        read_only_fields = ("id", "date_joined", "last_login")

    def validate_username(self, value):
        user = User.objects.filter(username=value)
        if value == "admin":
            raise serializers.ValidationError("Username already exists")
        elif value == "mahan":
            raise serializers.ValidationError("Username can't be admin")
        elif len(value) <= 2:
            raise serializers.ValidationError(
                "Username must be at least 2 characters long"
            )
        return value

    def validate(self, data):
        passwords = data["password"]
        passwords2 = data["password2"]
        password_format(passwords, passwords2)
        return data

    def create(self, validated_data):
        User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
        )
        return validated_data


class UserEditProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        exclude = ["password", "username"]


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
            password_format(passwords, passwords2)
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
        password_format(passwords, passwords2)
        return data
