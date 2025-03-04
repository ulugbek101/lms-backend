from uuid import uuid4
from decimal import Decimal
from datetime import date

from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

from api.utils import LessonDays
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from phonenumber_field.modelfields import PhoneNumberField

from .validators import group_price_validator
from .utils import UserRoles
from .managers import (
    UserManager,
    SuperuserManager,
    AdminManager,
    TeacherManager,
    ParentManager,
    StudentManager,
)


class Room(models.Model):
    """
    Represents a classroom in the school
    """

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


class Expense(models.Model):
    """
    Represents expenses made by stuff
    """

    id = models.UUIDField(default=uuid4, primary_key=True, unique=True, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    assigned_by = models.ForeignKey(to="User", on_delete=models.SET_NULL, null=True, related_name='assigned_expenses')
    assigned_to = models.ForeignKey(to="User", on_delete=models.SET_NULL, null=True, related_name='user_expenses')
    assigned_by_name = models.CharField(max_length=255, null=True, blank=True)
    assigned_to_name = models.CharField(max_length=255, null=True, blank=True)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    description = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"{self.assigned_to if self.assigned_to else self.assigned_to_name} - {self.amount} - {self.created}"


class Subject(models.Model):
    """
    Represents a subject taught in a group
    """

    id = models.UUIDField(default=uuid4, primary_key=True, unique=True, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name", "-created"]

    def __str__(self):
        return self.name


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
    parent_students = models.ManyToManyField(to="Student", blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "middle_name", "phone_number"]

    objects = UserManager()

    class Meta:
        ordering = ["-created"]
        unique_together = [
            ["first_name", "last_name", "middle_name"]
        ]

    def __str__(self):
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
        return f"{self.first_name.capitalize()} {self.last_name.capitalize()} {self.middle_name.capitalize()}"

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


class Lesson(models.Model):
    """
    Represents each lesson for particular group
    """

    id = models.UUIDField(default=uuid4, primary_key=True, unique=True, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    group = models.ForeignKey(to="Group", on_delete=models.CASCADE)
    theme = models.CharField(max_length=255)
    room = models.ForeignKey("Room", on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"{self.group.name} - {self.theme} - {self.created}"


class Homework(models.Model):
    """
    Represents homework for each lesson
    """

    def get_upload_path(self):
        return f"lessons/{self.lesson.group.name}"

    id = models.UUIDField(default=uuid4, primary_key=True, unique=True, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    lesson = models.ForeignKey(to=Lesson, on_delete=models.CASCADE)
    file = models.FileField(upload_to=get_upload_path, null=True, blank=True)
    description = models.TextField()
    deadline = models.DateTimeField()

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"{self.lesson.theme} - {self.deadline}"


class Group(models.Model):
    """
    Represents a study group led by a teacher for a specific subject
    """

    id = models.UUIDField(default=uuid4, primary_key=True, unique=True, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    subject = models.ForeignKey(to=Subject, on_delete=models.PROTECT)
    teacher = models.ForeignKey(to="Teacher", on_delete=models.PROTECT)
    name = models.CharField(max_length=255, unique=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, validators=[group_price_validator])
    lesson_days = models.CharField(max_length=255, choices=LessonDays.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    # @property
    # def has_active_lesson(self):
    #     """Checks if a lesson is currently active."""
    #     now_time = timezone.localtime().time()
    #     return self.start_time <= now_time <= self.end_time


class Superuser(User):
    """
    Proxy model for Superadmins with role assignment
    """

    objects = SuperuserManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        self.role = UserRoles.SUPERUSER
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


class Attendance(models.Model):
    """
    Represents attendance of a Student, whether student is absent or not
    """

    id = models.UUIDField(default=uuid4, primary_key=True, unique=True, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_absent = models.BooleanField(default=True)
    student = models.ForeignKey(to=Student, on_delete=models.CASCADE)
    lesson = models.ForeignKey(to=Lesson, on_delete=models.CASCADE)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"{self.student.full_name} - {self.lesson.created} - {not self.is_absent}"


class Payment(models.Model):
    """
    Represents a payment record for a student in a group
    """

    id = models.UUIDField(default=uuid4, primary_key=True, unique=True, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    year = models.IntegerField(default=date.today().year)
    month = models.IntegerField(default=date.today().month)
    student = models.ForeignKey(to=Student, on_delete=models.SET_NULL, null=True)
    group = models.ForeignKey(to="Group", on_delete=models.SET_NULL, null=True)
    student_name = models.CharField(max_length=255, null=True, blank=True)
    group_name = models.CharField(max_length=255, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["-year", "-month", "-amount"]
        unique_together = ["student", "year", "month"]

    def __str__(self):
        return f"{self.student.full_name} - {self.month + 1}/{self.year} - {self.amount} so'm"

    class Meta:
        ordering = ["-created"]


class Point(models.Model):
    """
    Represents point each Student would get for accomplishing homeworks
    """

    id = models.UUIDField(default=uuid4, primary_key=True, unique=True, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    student = models.ForeignKey(to=Student, on_delete=models.CASCADE)
    homework = models.ForeignKey(to=Homework, on_delete=models.CASCADE)
    amount = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])

    def __str__(self):
        return f"{self.amount} - {self.student.full_name} - {self.homework.lesson.theme}"
