from rest_framework.viewsets import ModelViewSet
from accounts_app.Serializers import *
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.generics import UpdateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.cache import cache
from accounts_app.utils import generate_code
from rest_framework import status


class UserViewSet(ModelViewSet):
    """
    Post :
        for create new user and get username and password for create user
    retrieve:
        if user is admin see all user for id_user but is not see self
    list :
        if user is admin see all user
    put or delete :
        if user is admin put or delete all user but is not admin see self
    """

    queryset = User.objects.all()
    serializer_class = UserCreateSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [AllowAny()]
        elif self.action == "list":
            return [IsAdminUser()]
        else:
            return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "list":
            return UserListSerializer
        elif self.action == "retrieve":
            return UserRetrieveSerializer
        elif self.action in ["update", "partial_update"]:
            if self.request.user.is_staff:
                return AdminUserUpdateSerializer
            return UserUpdateSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)


class ChangePasswordViewSet(UpdateAPIView):
    """
    user can change self password
    """

    queryset = User.objects.all()
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        return user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object(), data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"result": "ok"}, status=status.HTTP_200_OK)


class ForgetPasswordView(APIView):
    """
    send otp code for valid user
    """

    def post(self, request):
        serializer = ForgetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.instance
        if user:
            # sendsms()
            cache.set(
                serializer.validated_data["username"],
                {
                    "username": serializer.validated_data["username"],
                    "code": generate_code(),
                },
                timeout=180,
            )
        return Response({"detail": "send code for reset password"})


class VerifyCodeView(APIView):
    """
    change password by otp code
    """

    def post(self, request):
        serializer = VerifyCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.change_password()
        return Response({"result": "ok"})
