from django.db import models


class UserRoles(models.TextChoices):
    SUPERADMIN = "superadmin", "Superuser"
    ADMIN = "admin", "Administrator"
    TEACHER = "teacher", "Ustoz"
    PARENT = "parent", "Ota-ona"
    STUDENT = "student", "O'quvchi"
