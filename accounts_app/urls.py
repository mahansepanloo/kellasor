from accounts_app.views import (
    UserViewSet,
    ChangePasswordViewSet,
    ForgetPasswordView,
    VerifyCodeView,
)
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
    TokenBlacklistView,
    TokenObtainPairView,
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")

app_name = "accounts"

urlpatterns = [
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("token/blacklist/", TokenBlacklistView.as_view(), name="token_blacklist"),
    path("reset-password/", ChangePasswordViewSet.as_view(), name="reset_password"),
    path("forget-password/", ForgetPasswordView.as_view(), name="forget_password"),
    path("verify-code/", VerifyCodeView.as_view(), name="verify_code"),
] + router.urls
