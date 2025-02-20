from uuid import uuid4
from datetime import date
from decimal import Decimal

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from .roles import UserRoles
from .managers import UserManager, SuperAdminManager, AdminManager, TeacherManager, ParentManager, StudentManager
from .validators import group_price_validator


class Payment(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True, unique=True, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    year = models.IntegerField(default=date.today().year)
    month = models.IntegerField(default=date.today().month)
    # student_id = models.CharField(max_length=255)
    # group_id = models.CharField(max_length=255)
    student = models.ForeignKey(to="Student", on_delete=models.SET_NULL, null=True)
    group = models.ForeignKey(to="Group", on_delete=models.SET_NULL, null=True)
    student_fullname = models.CharField(max_length=255, null=True, blank=True)
    group_name = models.CharField(max_length=255, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.student_id} - {self.month + 1}/{self.year} - {self.amount} so'm"

    class Meta:
        ordering = ["-year", "-month", "-amount"]
        unique_together = ['student_id', 'year', 'month']


class User(AbstractBaseUser, PermissionsMixin):
    """ Base User model for a system """
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
    # student_group = models.ForeignKey(to="Group", on_delete=models.PROTECT, null=True, blank=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "middle_name"]
    objects = UserManager()

    class Meta:
        ordering = ["-created", "first_name", "last_name"]
        unique_together = [
            ["first_name", "last_name", "middle_name"],
        ]

    def __str__(self) -> str:
        """ string representation of a User """
        return f"{self.first_name} {self.last_name}"

    @property
    def get_role_name(self):
        """ Returns human-readable role name of a User"""
        return self.get_role_display()

    @property
    def full_name(self):
        """ Returns full name of a User """
        return f"{self.first_name} {self.last_name}"

    @property
    def is_fully_paid(self) -> tuple[bool, Decimal]:
        """Returns (bool, decimal):
        - True & amount if fully paid,
        - False & amount if partially paid,
        - False & 0 if no payment.
        """
        current_year, current_month = date.today().year, date.today().month

        payment: Payment = Payment.objects.filter(
            student=self, year=current_year, month=current_month
        ).first()

        if not payment:
            return False, Decimal(0)

        if payment.student.is_preferential:
            group_price = payment.group.price
        else:
            group_price = payment.student.preferential_amount

        if payment.amount >= group_price:
            return True, Decimal(payment.amount)
        return False, Decimal(payment.amount)


class SuperAdmin(User):
    """ Proxy model for Superadmins """
    objects = SuperAdminManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        """ Overriding save method to handle role re-assignment for Superadmins """
        self.role = UserRoles.SUPERADMIN
        super().save(*args, **kwargs)


class Admin(User):
    """ Proxy model for Admins """
    objects = AdminManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        """ Overriding save method to handle role re-assignment for Admins """
        self.role = UserRoles.ADMIN
        super().save(*args, **kwargs)


class Teacher(User):
    """ Proxy model for Teachers """
    objects = TeacherManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        """ Overriding save method to handle role re-assignment for Teachers """
        self.role = UserRoles.TEACHER
        super().save(*args, **kwargs)


class Student(User):
    """ Proxy model for Students """
    objects = StudentManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        self.role = UserRoles.STUDENT
        super().save(*args, **kwargs)


class Parent(User):
    objects = ParentManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        """ Overriding save method to handle role re-assignment for Parents """
        self.role = UserRoles.PARENT
        super().save(*args, **kwargs)


class Subject(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True, unique=True, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Group(models.Model):
    id = models.UUIDField(default=uuid4, primary_key=True, unique=True, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    subject = models.ForeignKey(to=Subject, on_delete=models.PROTECT)
    teacher = models.ForeignKey(to=Teacher, on_delete=models.PROTECT)
    name = models.CharField(max_length=255, unique=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, validators=[group_price_validator])

    def __str__(self):
        return self.name
