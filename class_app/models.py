from django.db import models
from utls.models import BaseModel
from utls.func import generator, generator_password


class ClassRooms(BaseModel):
    code = models.CharField(max_length=255, unique=True, default=generator)
    name = models.CharField(max_length=255)
    class_type = models.CharField(
        max_length=255, choices=(("private", "Private"), ("public", "Public"))
    )
    description = models.TextField(null=True, blank=True)
    capacity = models.IntegerField(null=True, blank=True)
    access_type = models.CharField(
        max_length=255, choices=(("email", "Email"), ("password", "Password"))
    )
    password = models.CharField(max_length=255, null=True, blank=True)
    start_join_date = models.DateTimeField(null=True, blank=True)
    end_join_date = models.DateTimeField(null=True, blank=True)
    teacher = models.ManyToManyField(
        "accounts_app.User", related_name="classrooms_as_teacher"
    )
    mentor = models.ManyToManyField(
        "accounts_app.User", related_name="classrooms_as_mentor", blank=True
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.teacher.count() < 1:
            raise ValueError("Teacher can only be one")
        if not self.password:  
            if self.class_type == "private" and self.access_type == "password":
                self.password = generator_password(5)
            elif self.class_type == "public" and self.access_type == "email":
                self.password = generator_password(50)
        super().save(*args, **kwargs)


class Students(BaseModel):
    student = models.ManyToManyField(
        "accounts_app.User", related_name="classrooms_as_student", blank=True
    )
    class_room = models.ForeignKey(
        ClassRooms, on_delete=models.CASCADE, related_name="students"
    )

    def __str__(self):
        return self.class_room.name
