from uuid import uuid4
from datetime import date
from decimal import Decimal

from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from .utils import UserRoles, LessonDays
from .managers import (
    UserManager,
    SuperAdminManager,
    AdminManager,
    TeacherManager,
    ParentManager,
    StudentManager,
)
from .validators import group_price_validator


class Payment(models.Model):
    """Represents a payment record for a student in a group."""

    id = models.UUIDField(default=uuid4, primary_key=True, unique=True, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    year = models.IntegerField(default=date.today().year)
    month = models.IntegerField(default=date.today().month)
    student = models.ForeignKey("Student", on_delete=models.SET_NULL, null=True)
    group = models.ForeignKey("Group", on_delete=models.SET_NULL, null=True)
    student_fullname = models.CharField(max_length=255, null=True, blank=True)
    group_name = models.CharField(max_length=255, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        ordering = ["-year", "-month", "-amount"]
        unique_together = ["student", "year", "month"]

    def __str__(self):
        return f"{self.student.full_name} - {self.month + 1}/{self.year} - {self.amount} so'm"


class User(AbstractBaseUser, PermissionsMixin):
    """Base model for all user types, extending Django's AbstractBaseUser."""

    id = models.UUIDField(default=uuid4, primary_key=True, unique=True, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_preferential = models.BooleanField(default=False)
    preferential_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    role = models.CharField(max_length=10, choices=UserRoles.choices)
    parent_children = models.ManyToManyField(to="self", blank=True)
    student_groups = models.ManyToManyField(to="Group", blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "middle_name"]

    objects = UserManager()

    class Meta:
        ordering = ["-created", "first_name", "last_name"]
        unique_together = [["first_name", "last_name", "middle_name"]]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def get_role_name(self):
        """Returns the human-readable role name."""
        return self.get_role_display()

    @property
    def full_name(self):
        """Returns the full name of the user."""
        return f"{self.first_name.capitalize()} {self.last_name.capitalize()}"

    @property
    def is_fully_paid(self) -> tuple[bool, Decimal]:
        """Returns (bool, decimal) indicating whether the student is fully paid."""
        current_year, current_month = date.today().year, date.today().month

        payment = Payment.objects.filter(student=self, year=current_year, month=current_month).first()

        if not payment:
            return False, Decimal(0)

        group_price = payment.student.preferential_amount if self.is_preferential else payment.group.price

        return (payment.amount >= group_price, Decimal(payment.amount))


class SuperAdmin(User):
    """Proxy model for Superadmins with role assignment."""

    objects = SuperAdminManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        self.role = UserRoles.SUPERADMIN
        super().save(*args, **kwargs)


class Admin(User):
    """Proxy model for Admins with role assignment."""

    objects = AdminManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        self.role = UserRoles.ADMIN
        super().save(*args, **kwargs)


class Teacher(User):
    """Proxy model for Teachers with role assignment."""

    objects = TeacherManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        self.role = UserRoles.TEACHER
        super().save(*args, **kwargs)


class Student(User):
    """Proxy model for Students with role assignment."""

    objects = StudentManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        self.role = UserRoles.STUDENT
        super().save(*args, **kwargs)


class Parent(User):
    """Proxy model for Parents with role assignment."""

    objects = ParentManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        self.role = UserRoles.PARENT
        super().save(*args, **kwargs)


class Subject(models.Model):
    """Represents a subject taught in a group."""

    id = models.UUIDField(default=uuid4, primary_key=True, unique=True, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Group(models.Model):
    """Represents a study group led by a teacher for a specific subject."""

    id = models.UUIDField(default=uuid4, primary_key=True, unique=True, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    subject = models.ForeignKey(to=Subject, on_delete=models.PROTECT)
    teacher = models.ForeignKey(to=Teacher, on_delete=models.PROTECT)
    name = models.CharField(max_length=255, unique=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, validators=[group_price_validator])
    room = models.ForeignKey("Room", on_delete=models.SET_NULL, null=True)
    lesson_days = models.CharField(max_length=255, choices=LessonDays.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ["created"]

    def __str__(self):
        return self.name

    @property
    def has_active_lesson(self):
        """Checks if a lesson is currently active."""
        now_time = timezone.localtime().time()
        return self.start_time <= now_time <= self.end_time


class Room(models.Model):
    """Represents a classroom in the school."""

    id = models.UUIDField(default=uuid4, primary_key=True, unique=True, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    alias_name = models.CharField(max_length=255, null=True, blank=True)
    number = models.IntegerField(unique=True)
    floor = models.IntegerField(default=3)

    class Meta:
        ordering = ["number"]

    def __str__(self):
        return self.alias_name if self.alias_name else str(self.number)
