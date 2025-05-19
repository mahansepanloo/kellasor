from django.shortcuts import render
from .models import ClassRooms, Students
from accounts_app.models import User
from rest_framework.viewsets import ModelViewSet
from .Serializer import *
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.cache import cache
from rest_framework.generics import *
from rest_framework import status


class ClassRoomViewSet(ModelViewSet):
    queryset = ClassRooms.objects.all()
    serializer_class = ClassRoomCreatedSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer(self, *args, **kwargs):
        if self.action == "list":
            return ClassRoomListSerializer(*args, **kwargs)
        elif self.action == "retrieve":
            return ClassRoomEditSerializer(*args, **kwargs)
        elif self.action in ["put", "patch"]:
            return ClassRoomCreatedSerializer(*args, **kwargs)
        else:
            return super().get_serializer(*args, **kwargs)

    def get_queryset(self):
        if self.request.user.is_superuser:
            return ClassRooms.objects.all().prefetch_related("students", "mentor")
        else:
            return ClassRooms.objects.filter(
                teacher=self.request.user
            ).prefetch_related("students", "mentor")

    def perform_create(self, serializer):
        serializer.save(teacher=[self.request.user], created_by=self.request.user)


class JoinView(APIView):
    permission_classes = [IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        try:
            self.class_room = ClassRooms.objects.get(id=kwargs["pk_id"])
        except ClassRooms.DoesNotExist:
            return Response(
                {"error": "Classroom not found"}, status=status.HTTP_404_NOT_FOUND
            )
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if self.class_room.class_type == "public":
            students, _ = Students.objects.get_or_create(class_room=self.class_room)
            students.student.add(self.request.user)
            return Response({"message": "You have joined the class"}, status=200)
        else:
            return Response(
                {"error": "You are not allowed to join this class"}, status=403
            )

    def post(self, request, *args, **kwargs):
        if self.class_room.class_type != "privet":
            return Response(
                {"error": "You are not allowed to join this class"},
                status=status.HTTP_403_FORBIDDEN,
            )

        students, _ = Students.objects.get_or_create(class_room=self.class_room)

        if self.class_room.access_type == "password":
            serializer = PasswordSerializer(data=request.data)
            if serializer.is_valid():
                password = serializer.validated_data.get("password")
                if self.class_room.passwords == password:
                    students.student.add(request.user)
                    return Response(
                        {"message": "You have joined the class"},
                        status=status.HTTP_200_OK,
                    )
                return Response(
                    {"error": "Password is incorrect"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif self.class_room.access_type == "email":
            pin = request.query_params.get("pinvalidate")
            if self.class_room.passwords == pin:
                students.student.add(request.user)
                return Response(
                    {"message": "You have joined the class"}, status=status.HTTP_200_OK
                )
            return Response(
                {"error": "Pin is incorrect"}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"error": "You are not allowed to join this class"},
            status=status.HTTP_403_FORBIDDEN,
        )
