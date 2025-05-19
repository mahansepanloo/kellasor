from accounts_app.views import *
from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
    TokenBlacklistView,
    TokenObtainPairView,
)
from rest_framework.routers import DefaultRouter
from class_app.views import ClassRoomViewSet, JoinView

router = DefaultRouter()
router.register(r'classrooms', ClassRoomViewSet)

app_name = "class"

urlpatterns = [
    path("api/join-classroom/", JoinView.as_view(), name="join-classroom"),

] + router.urls
