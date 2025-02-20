from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model

from .models import Subject
from .roles import UserRoles

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
    def setUp(self):
        self.subject1 = Subject.objects.create(name="Matematika")
        self.subject2 = Subject.objects.create(name="Fizika")

    def test_subject_creation(self):
        self.assertEqual(self.subject1.name, "Matematika")
        self.assertEqual(self.subject2.name, "Fizika")

    def test_subject_name_duplicate_error(self):
        """Ensure duplicate subject names raise an IntegrityError"""
        with self.assertRaises(IntegrityError):
            Subject.objects.create(name="Fizika")
