from rest_framework.permissions import BasePermission
from class_app.models import ClassRooms
from rest_framework.exceptions import NotFound


class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        class_id = view.kwargs.get("pk")
        if not class_id:
            return False

        try:
            class_room = ClassRooms.objects.get(id=class_id)
        except ClassRooms.DoesNotExist:
            raise NotFound("not found classroom")

        return request.user in class_room.teacher.all()
