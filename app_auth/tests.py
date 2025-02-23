from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model

from .models import Subject, Group, Payment
from .utils import UserRoles

User = get_user_model()


class UserModelTest(TestCase):
    """Test User model and its role assignment"""

    def test_superadmin_creation(self):
        """Test SuperAdmin role is correctly assigned"""
        superadmin = User.objects.create_user(
            email="superadmin@example.com",
            first_name="Super",
            last_name="Admin",
            middle_name="Black",
            password="password",
            role="superadmin",
        )
        self.assertEqual(superadmin.role, UserRoles.SUPERADMIN)
        self.assertTrue(superadmin.check_password("password"))

    def test_admin_creation(self):
        """Test Admin role is correctly assigned"""
        admin = User.objects.create_user(
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            middle_name="Black",
            password="password",
            role="admin",
        )
        self.assertEqual(admin.role, UserRoles.ADMIN)
        self.assertTrue(admin.check_password("password"))

    def test_teacher_creation(self):
        """Test Teacher role is correctly assigned"""
        teacher = User.objects.create_user(
            email="teacher@example.com",
            first_name="Teacher",
            last_name="User",
            middle_name="Black",
            password="password",
            role="teacher",
        )
        self.assertEqual(teacher.role, UserRoles.TEACHER)
        self.assertTrue(teacher.check_password("password"))

    def test_student_creation(self):
        """Test Student role is correctly assigned"""
        student = User.objects.create_user(
            email="student@example.com",
            first_name="Student",
            last_name="User",
            middle_name="Black",
            password="password",
            role="student",
        )
        self.assertEqual(student.role, UserRoles.STUDENT)
        self.assertTrue(student.check_password("password"))

    def test_parent_creation(self):
        """Test Parent role is correctly assigned"""
        parent = User.objects.create_user(
            email="parent@example.com",
            first_name="Parent",
            last_name="User",
            middle_name="Black",
            password="password",
            role="parent",
        )
        self.assertEqual(parent.role, UserRoles.PARENT)
        self.assertTrue(parent.check_password("password"))

    def test_missing_email_raises_validation_error(self):
        """Test that creating a user without email raises ValidationError"""
        with self.assertRaises(ValidationError) as context:
            User.objects.create_user(
                email="",
                first_name="John",
                last_name="Doe",
                middle_name="Black",
                password="password"
            )
        self.assertEqual(str(context.exception), "['Users must have email address']")

    def test_missing_first_name_raises_validation_error(self):
        """Test that creating a user without first name raises ValidationError"""
        with self.assertRaises(ValidationError) as context:
            User.objects.create_user(
                email="user@example.com",
                first_name="",
                last_name="Doe",
                middle_name="Black",
                password="password"
            )
        self.assertEqual(str(context.exception), "['Users must have first name']")

    def test_missing_last_name_raises_validation_error(self):
        """Test that creating a user without last name raises ValidationError"""
        with self.assertRaises(ValidationError) as context:
            User.objects.create_user(
                email="user@example.com",
                first_name="John",
                last_name="",
                middle_name="Black",
                password="password"
            )
        self.assertEqual(str(context.exception), "['Users must have last name']")

    def test_missing_middle_name_raises_validation_error(self):
        """Test that creating a user without middle name raises ValidationError"""
        with self.assertRaises(ValidationError) as context:
            User.objects.create_user(
                email="user@example.com",
                first_name="John",
                last_name="Doe",
                middle_name="",
                password="password"
            )
        self.assertEqual(str(context.exception), "['Users must have middle name']")


class SubjectModelTest(TestCase):
    """ Test Subject model and its creation """

    def test_create_subject(self):
        """ Test subject creation """
        subject = Subject.objects.create(name="Matematika")
        self.assertEqual(subject.name, "Matematika")

    def test_subject_name_duplicate_error(self):
        """Ensure duplicate subject names raise an IntegrityError"""
        with self.assertRaises(IntegrityError):
            Subject.objects.create(name="Matematika")
            Subject.objects.create(name="Matematika")


class GroupModelTest(TestCase):
    """ Test Group model and its creation """

    def setUp(self):
        """ Setup group details and create group instance """
        self.student = User.objects.create_user(first_name="Student John",
                                                last_name="Student Doe",
                                                middle_name="Student Black",
                                                email="studentjohndoe@gmail.com",
                                                role="student")
        self.group_data = {
            "subject": Subject.objects.create(name="Matematika"),
            "teacher": User.objects.create_user(first_name="John",
                                                last_name="Doe",
                                                middle_name="Black",
                                                email="johndoe@gmail.com",
                                                role="teacher"),
            "name": "Matematika tayyorlov",
            "price": 300000.00
        }
        self.group = Group.objects.create(**self.group_data)
        self.student.student_groups.add(self.group)

    def test_group_attributes(self):
        """ Test to check if group attributes set correctly """
        self.assertTrue(self.group)
        self.assertEqual(self.group.name, self.group_data["name"])
        self.assertEqual(self.group.price, self.group_data["price"])
        self.assertEqual(self.group.teacher, self.group_data["teacher"])
        self.assertEqual(self.group.subject, self.group_data["subject"])

    def test_student_has_group(self):
        """ Test to check whether group added to student's groups list """
        self.assertTrue(self.student.student_groups.filter(id=self.group.id).exists())


class PaymentModelTest(TestCase):
    def setUp(self):
        """ Setup payment details and create payment instance """
        self.group_data = {
            "subject": Subject.objects.create(name="Matematika"),
            "teacher": User.objects.create_user(first_name="John",
                                                last_name="Doe",
                                                middle_name="Black",
                                                email="johndoe@gmail.com",
                                                role="teacher"),
            "name": "Matematika tayyorlov",
            "price": 300000.00
        }
        self.payment_data = {
            "year": 2024,
            "month": 12,
            "student": User.objects.create_user(first_name="Student John",
                                                last_name="Student Doe",
                                                middle_name="Student Black",
                                                email="studentjohndoe@gmail.com",
                                                role="student"),
            "group": Group.objects.create(**self.group_data),
            "amount": 300000.00
        }
        self.payment = Payment.objects.create(**self.payment_data)

    def test_payment_attributes(self):
        """ Test to check if payment attributes set correctly """
        self.assertTrue(self.payment)
        self.assertEqual(self.payment.year, self.payment_data["year"])
        self.assertEqual(self.payment.month, self.payment_data["month"])
        self.assertEqual(self.payment.student, self.payment_data["student"])
        self.assertEqual(self.payment.group, self.payment_data["group"])
        self.assertEqual(self.payment.amount, self.payment_data["amount"])
        self.assertEqual(self.payment.student_fullname, None)
        self.assertEqual(self.payment.group_name, None)

