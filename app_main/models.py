from uuid import uuid4
from datetime import date

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

from app_auth.models import User, Teacher, Student, Parent
from app_auth.utils import LessonDays
from .validators import group_price_validator


class Expense(models.Model):
    """
    Represents expenses made by stuff
    """

    id = models.UUIDField(default=uuid4, primary_key=True, unique=True, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    assigned_by = models.ForeignKey(to=User, on_delete=models.SET_NULL)
    assigned_to = models.ForeignKey(to=User, on_delete=models.SET_NULL)
    assigned_by_name = models.CharField(max_length=255, null=True, blank=True)
    assigned_to_name = models.CharField(max_length=255, null=True, blank=True)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    description = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"{self.assigned_to if self.assigned_to else self.assigned_to_name} - {self.amount} - {self.created}"

    # TODO: Create signals to set assigned_to_name, assigned_by_name on assigned_by, assigned_to delete


class Payment(models.Model):
    """
    Represents a payment record for a student in a group
    """

    id = models.UUIDField(default=uuid4, primary_key=True, unique=True, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    year = models.IntegerField(default=date.today().year)
    month = models.IntegerField(default=date.today().month)
    student = models.ForeignKey("Student", on_delete=models.SET_NULL, null=True)
    group = models.ForeignKey("Group", on_delete=models.SET_NULL, null=True)
    student_name = models.CharField(max_length=255, null=True, blank=True)
    group_name = models.CharField(max_length=255, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["-year", "-month", "-amount"]
        unique_together = ["student", "year", "month"]

    def __str__(self):
        return f"{self.student.full_name} - {self.month + 1}/{self.year} - {self.amount} so'm"

    # TODO: Create signals to set student_name, group_name on student, group delete


class Subject(models.Model):
    """
    Represents a subject taught in a group
    """

    id = models.UUIDField(default=uuid4, primary_key=True, unique=True, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name", "-ordering"]

    def __str__(self):
        return self.name


class Group(models.Model):
    """
    Represents a study group led by a teacher for a specific subject
    """

    id = models.UUIDField(default=uuid4, primary_key=True, unique=True, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    subject = models.ForeignKey(to=Subject, on_delete=models.PROTECT)
    teacher = models.ForeignKey(to=Teacher, on_delete=models.PROTECT)
    name = models.CharField(max_length=255, unique=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, validators=[group_price_validator])
    lesson_days = models.CharField(max_length=255, choices=LessonDays.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return self.name

    # @property
    # def has_active_lesson(self):
    #     """Checks if a lesson is currently active."""
    #     now_time = timezone.localtime().time()
    #     return self.start_time <= now_time <= self.end_time


class Lesson(models.Model):
    """
    Represents each lesson for particular group
    """

    id = models.UUIDField(default=uuid4, primary_key=True, unique=True, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    group = models.ForeignKey(to=Group, on_delete=models.CASCADE)
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
    deadline = models.DateTimeField(validators=[
        lambda deadline_date: deadline_date > timezone.now()
    ])

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"{self.lesson.theme} - {self.deadline}"


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
