from django.contrib import admin
from .models import ClassRooms, Students
from django.contrib.admin import register

from django.contrib import admin
from class_app.models import ClassRooms, Students


@admin.register(ClassRooms)
class ClassRoomAdmin(admin.ModelAdmin):
    search_fields = ["name", "teacher__username", "mentor__username"]
    list_display = [
        "name",
        "class_type",
        "capacity",
        "access_type",
    ]
    filter_horizontal = ["mentor", "teacher"]


@admin.register(Students)
class StudentAdmin(admin.ModelAdmin):
    search_fields = ["class_room__name", "student__username"]
    autocomplete_fields = ["class_room"]
    filter_horizontal = ["student"]
