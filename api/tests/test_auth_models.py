from datetime import timedelta

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model
from django.utils import timezone

from api.models import Subject, Group, Payment
from api.utils import UserRoles, LessonDays

User = get_user_model()


class UserModelTest(TestCase):
    """
    Test User model and other related proxy models (Admin, Teacher, Parent, Student)
    """

    def setUp(self):
        self.data = {
            "email": "user@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "middle_name": "Black",
            "phone_number": "+998996937308",
            "password": "password",
            "role": UserRoles.SUPERUSER,
        }

    def test_create_superuser(self):
        """
        Test User is created correctly and roles are assigned correctly
        """
        user = User.objects.create_user(**self.data)

        self.assertEqual(user.email, self.data["email"])
        self.assertEqual(user.first_name, self.data["first_name"])
        self.assertEqual(user.last_name, self.data["last_name"])
        self.assertEqual(user.middle_name, self.data["middle_name"])
        self.assertEqual(user.phone_number, self.data["phone_number"])
        self.assertEqual(user.role, UserRoles.SUPERUSER)
        self.assertTrue(user.check_password(self.data["password"]))

        # Role changes
        for role in [UserRoles.ADMIN, UserRoles.TEACHER, UserRoles.PARENT, UserRoles.STUDENT]:
            user.role = role
            user.save()
            self.assertEqual(user.role, role)

    def test_missing_fields_raises_validation_error(self):
        """
        Test missing fields raise ValidationErrors
        """
        required_fields = ["email", "first_name", "last_name", "middle_name", "phone_number"]

        for field in required_fields:
            data = self.data.copy()
            data[field] = ""
            user = User(**data)
            with self.assertRaises(ValidationError, msg=f"Users must have {field} field"):
                user.full_clean()


class SubjectModelTest(TestCase):
    """
    Test Subject model and its creation
    """

    def test_create_subject(self):
        """
        Test subject creation
        """
        subject = Subject.objects.create(name="Matematika")
        self.assertEqual(subject.name, "Matematika")

    def test_subject_name_duplicate_error(self):
        """
        Test if duplicate subject names raise an IntegrityError
        """
        with self.assertRaises(IntegrityError):
            Subject.objects.create(name="Matematika")
            Subject.objects.create(name="Matematika")


class GroupModelTest(TestCase):
    """
    Test Group model and its creation
    """

    def setUp(self):
        """
        Setup group details and create group instance
        """
        self.student = User.objects.create_user(first_name="Student John",
                                                last_name="Student Doe",
                                                middle_name="Student Black",
                                                phone_number="+998996937308",
                                                email="studentjohndoe@gmail.com",
                                                role="student")
        self.group_data = {
            "subject": Subject.objects.create(name="Matematika"),
            "teacher": User.objects.create_user(first_name="John",
                                                last_name="Doe",
                                                middle_name="Black",
                                                phone_number="+998996937308",
                                                email="johndoe@gmail.com",
                                                role="teacher"),
            "name": "Matematika tayyorlov",
            "price": 300000.00,
            "start_time": timezone.now().time(),
            "end_time": timezone.now().time(),
            "start_date": timezone.now().date(),
            "end_date": timezone.now().date(),
            "lesson_days": LessonDays.ODD,
        }
        self.group = Group.objects.create(**self.group_data)
        self.student.student_groups.add(self.group)

    def test_group_fields(self):
        """ Test to check if group attributes set correctly """
        self.assertTrue(self.group)
        self.assertEqual(self.group.name, self.group_data["name"])
        self.assertEqual(self.group.price, self.group_data["price"])
        self.assertEqual(self.group.teacher, self.group_data["teacher"])
        self.assertEqual(self.group.subject, self.group_data["subject"])
        self.assertEqual(self.group.lesson_days, LessonDays.ODD)

    def test_student_in_group(self):
        """ Test to check whether group added to student's groups list """
        self.assertTrue(self.student.student_groups.filter(id=self.group.id).exists())


class PaymentModelTest(TestCase):
    def setUp(self):
        """
        Setup payment details and create payment instance
        """
        self.group_data = {
            "subject": Subject.objects.create(name="Matematika"),
            "teacher": User.objects.create_user(first_name="John",
                                                last_name="Doe",
                                                middle_name="Black",
                                                phone_number="+998996937308",
                                                email="johndoe@gmail.com",
                                                role="teacher"),
            "name": "Matematika tayyorlov",
            "price": 300000.00,
            "start_time": timezone.now().time(),
            "end_time": timezone.now().time(),
            "start_date": timezone.now().date(),
            "end_date": timezone.now().date(),
            "lesson_days": LessonDays.ODD,
        }
        self.payment_data = {
            "year": 2024,
            "month": 12,
            "student": User.objects.create_user(first_name="Student John",
                                                last_name="Student Doe",
                                                middle_name="Student Black",
                                                phone_number="+998996937308",
                                                email="studentjohndoe@gmail.com",
                                                role="student"),
            "group": Group.objects.create(**self.group_data),
            "amount": 300000.00
        }
        self.payment = Payment.objects.create(**self.payment_data)

    def test_payment_fields(self):
        """
        Test if payment fields set correctly
        """
        self.assertTrue(self.payment)
        self.assertEqual(self.payment.year, self.payment_data["year"])
        self.assertEqual(self.payment.month, self.payment_data["month"])
        self.assertEqual(self.payment.student, self.payment_data["student"])
        self.assertEqual(self.payment.group, self.payment_data["group"])
        self.assertEqual(self.payment.amount, self.payment_data["amount"])
        self.assertEqual(self.payment.student_name, self.payment.student.full_name)
        self.assertEqual(self.payment.group_name, self.payment.group.name)
