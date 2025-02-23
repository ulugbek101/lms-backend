from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError

from .utils import UserRoles


class UserManager(BaseUserManager):
    role = None

    def create_user(self, email, first_name, last_name, middle_name, password=None, **extra_fields):
        if not email:
            raise ValidationError("Users must have email address")

        if not first_name:
            raise ValidationError("Users must have first name")

        if not last_name:
            raise ValidationError("Users must have last name")

        if not middle_name:
            raise ValidationError("Users must have middle name")

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, middle_name, password, **extra_fields):
        user = self.create_user(email=email,
                                first_name=first_name,
                                last_name=last_name,
                                middle_name=middle_name,
                                password=password,
                                **extra_fields)
        user.is_staff = True
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(role=self.role) if self.role else queryset


class SuperAdminManager(UserManager):
    role = UserRoles.SUPERADMIN


class AdminManager(UserManager):
    role = UserRoles.ADMIN


class TeacherManager(UserManager):
    role = UserRoles.TEACHER


class ParentManager(UserManager):
    role = UserRoles.PARENT


class StudentManager(UserManager):
    role = UserRoles.STUDENT
