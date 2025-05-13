from .models import User
from rest_framework.viewsets import ModelViewSet
from .Serializer import *
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.cache import cache
from .validate import generate_code


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializerRegister

    def get_permissions(self):
        if self.request.method == "POST":
            return [AllowAny()]
        else:
            if self.request.user.is_authenticated:
                return [IsAdminUser()]
            return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "list":
            return UserSerializerList
        elif self.action == "retrieve":
            return UserSerializerRetrieve
        return super().get_serializer_class()


class EditUserView(RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserEditProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return User.objects.all()
        else:
            return User.objects.filter(id=self.request.user.id)


class ResetPasswordView(RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = ResetPasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return User.objects.all()
        else:
            return User.objects.filter(id=self.request.user.id)


class ForgetPasswordView(APIView):
    def post(self, request):
        serializer = ForgetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if User.objects.filter(
            username=serializer.validated_data["username"],
            phone=serializer.validated_data["phone"],
        ).exists():
            cache.set(
                serializer.validated_data["phone"],
                {
                    "username": serializer.validated_data["username"],
                    "code": generate_code(),
                },
                timeout=180,
            )
        return Response({"message": "send code for reset password"})


class VerifyCodeView(APIView):
    def post(self, request):
        serializer = VerifyCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cached_data = cache.get(serializer.validated_data["phone"])
        if not cached_data:
            return Response({"message": "not found code"})
        if cached_data["code"] != serializer.validated_data["code"]:
            return Response({"message": "code not correct "})

        user = User.objects.filter(username=cached_data["username"]).first()
        password = serializer.validated_data["password"]
        password_format(password, serializer.validated_data["password2"])
        user.set_password(password)
        user.save()

        cache.delete(serializer.validated_data["phone"])

        return Response({"message": "change password successful"})
