from uuid import uuid4
from datetime import date
from decimal import Decimal

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from phonenumber_field.modelfields import PhoneNumberField

from .utils import UserRoles
from .managers import (
    UserManager,
    SuperAdminManager,
    AdminManager,
    TeacherManager,
    ParentManager,
    StudentManager,
)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Base model for all user types, extending Django's AbstractBaseUser
    """

    id = models.UUIDField(default=uuid4, primary_key=True, unique=True, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255)
    phone_number = PhoneNumberField()
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_preferential = models.BooleanField(default=False)
    preferential_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    role = models.CharField(max_length=10, choices=UserRoles.choices)
    student_groups = models.ManyToManyField(to="Group", blank=True)
    student_parent = models.ForeignKey(to="Parent", blank=True, null=True, on_delete=models.SET_NULL)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "middle_name", "phone_number"]

    objects = UserManager()

    class Meta:
        ordering = ["-created"]
        unique_together = [
            ["first_name", "last_name", "middle_name"]
        ]

    def __str__(self):
        """
        String representaion of an object
        """
        return f"{self.first_name} {self.last_name} {self.middle_name}"

    @property
    def get_role_name(self):
        """
        Returns the human-readable role name
        """
        return self.get_role_display().capitalize()

    @property
    def full_name(self):
        """
        Returns the full name of the user
        """
        return f"{self.first_name.capitalize()} {self.last_name.capitalize()}"

    @property
    def is_fully_paid(self) -> tuple[bool, Decimal]:
        """
        Returns (bool, decimal) indicating whether the student is fully paid
        """
        if self.role != UserRoles.STUDENT:
            raise AttributeError(f"{self.__class__.__name__} object has no attribute 'is_fully_paid'")

        current_year, current_month = date.today().year, date.today().month

        payment = self.payment_set.filter(year=current_year, month=current_month).first()

        if not payment:
            return False, Decimal(0)

        group_price = payment.student.preferential_amount if self.is_preferential else payment.group.price

        return payment.amount >= group_price, Decimal(payment.amount)


class SuperAdmin(User):
    """
    Proxy model for Superadmins with role assignment
    """

    objects = SuperAdminManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        self.role = UserRoles.SUPERADMIN
        super().save(*args, **kwargs)


class Admin(User):
    """
    Proxy model for Admins with role assignment
    """

    objects = AdminManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        self.role = UserRoles.ADMIN
        super().save(*args, **kwargs)


class Teacher(User):
    """
    Proxy model for Teachers with role assignment
    """

    objects = TeacherManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        self.role = UserRoles.TEACHER
        super().save(*args, **kwargs)


class Student(User):
    """
    Proxy model for Students with role assignment
    """

    objects = StudentManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        self.role = UserRoles.STUDENT
        super().save(*args, **kwargs)


class Parent(User):
    """
    Proxy model for Parents with role assignment
    """

    objects = ParentManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        self.role = UserRoles.PARENT
        super().save(*args, **kwargs)
