from django.db import models


class UserRoles(models.TextChoices):
    SUPERUSER = "superuser", "Superuser"
    ADMIN = "admin", "Administrator"
    TEACHER = "teacher", "Ustoz"
    PARENT = "parent", "Ota-ona"
    STUDENT = "student", "O'quvchi"


class LessonDays(models.TextChoices):
    ODD = "1-3-5"
    EVEN = "2-4-6"
