from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from django.utils import timezone

from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField, HyperlinkedIdentityField
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from tutorial.quickstart.serializers import UserSerializer

from .models import Student, Group, Subject, Parent, Room, Teacher, Admin

User = get_user_model()


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom serializer to obtain JWT tokens with additional user information
    """

    @classmethod
    def get_token(cls, user):
        """
        Add custom claims to the token
        """
        token = super().get_token(user)
        token["email"] = user.email
        token["first_name"] = user.first_name
        token["last_name"] = user.last_name
        token["middle_name"] = user.middle_name
        token["role"] = user.get_role_name
        token["is_superuser"] = user.is_superuser
        token["is_staff"] = user.is_staff
        return token


class PasswordHashMixin:
    """
    Mixin to hash passwords before saving user instances
    """

    def create(self, validated_data):
        """
        Create user instance with hashed password.
        """
        password = validated_data.pop("password", None)
        user = self.Meta.model.objects.create_user(**validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AdminSerializer(PasswordHashMixin, ModelSerializer):
    """
    Serializer for Admin model with password hashing and field exclusion.
    """

    class Meta:
        model = Admin
        exclude = ["is_active", "is_superuser", "is_staff", "role", "last_login", "user_permissions", "groups",
                   "is_preferential", "preferential_amount",
                   "student_groups", "parent_students"]


class SubjectSerializer(ModelSerializer):
    """
    Serializer for Subject model
    """

    class Meta:
        model = Subject
        fields = "__all__"


class RoomSerializer(ModelSerializer):
    class Meta:
        model = Room
        fields = "__all__"


class StudentParentSerializer(ModelSerializer):
    """
    Nested serializer for Student's parent
    """

    class Meta:
        model = Parent
        fields = ["id", "first_name", "last_name", "middle_name", "email", "phone_number"]


class ParentSerializer(PasswordHashMixin, ModelSerializer):
    """
    Serializer for Parent model with password hashing and nested student relationship.
    """
    students = PrimaryKeyRelatedField(queryset=Student.objects.all(), many=True, required=False)

    class Meta:
        model = Parent
        exclude = ["is_active", "is_staff", "is_superuser", "role", "last_login", "user_permissions", "groups",
                   "is_preferential", "preferential_amount", "student_groups", "parent_students"]
        extra_kwargs = {
            "password": {
                "write_only": True
            }
        }

    def to_representation(self, instance):
        """
        Add nested student data to the serialized representation.
        """
        representation = super().to_representation(instance)
        representation["students"] = StudentSerializer(instance.parent_students.all(), many=True).data
        return representation

    def create(self, validated_data):
        """
        Create parent instance with student relationship.
        """
        students = validated_data.pop("students", [])
        parent = super().create(validated_data)

        if students:
            parent.parent_students.set(students)

        return parent


class TeacherSerializer(PasswordHashMixin, ModelSerializer):
    """
    Serializer for Teacher model with password hashing.
    """

    class Meta:
        model = Teacher
        exclude = ["is_active", "is_staff", "is_superuser", "role", "last_login", "user_permissions", "groups",
                   "parent_students", "student_groups", "is_preferential", "preferential_amount"]
        extra_kwargs = {
            "password": {
                "write_only": True
            }
        }


class GroupSerializer(ModelSerializer):
    """
    Serializer for Group model with subject and teacher nested representations.
    """
    subject = SubjectSerializer(many=False, read_only=True)
    teacher = TeacherSerializer(many=False, read_only=True)

    class Meta:
        model = Group
        fields = "__all__"

    def create(self, validated_data):
        """
        Automatically set group status based on start date.
        """
        start_date = validated_data.get("start_date")
        if start_date and start_date <= timezone.now().date():
            validated_data["is_active"] = True
        else:
            validated_data["is_active"] = False

        return super().create(validated_data)


class StudentSerializer(PasswordHashMixin, ModelSerializer):
    """
    Serializer for Student model with password hashing and nested relationships for groups and parents.
    """
    student_groups = PrimaryKeyRelatedField(queryset=Group.objects.all(), many=True, required=False)
    student_parents = PrimaryKeyRelatedField(queryset=Parent.objects.all(), many=True, required=False)

    class Meta:
        model = Student
        exclude = ["is_active", "is_staff", "is_superuser", "role", "last_login", "user_permissions", "groups",
                   "parent_students"]
        extra_kwargs = {
            "password": {
                "write_only": True
            }
        }

    def to_representation(self, instance):
        """
        Add nested group and parent data to the serialized representation.
        """
        representation = super().to_representation(instance)
        representation["student_groups"] = GroupSerializer(instance.student_groups.all(), many=True,
                                                           context=self.context).data
        representation["parents"] = StudentParentSerializer(instance.parents.all(), many=True,
                                                            context=self.context).data
        return representation

    def create(self, validated_data):
        """
        Create student instance with relationships to groups and parents.
        """
        student_groups = validated_data.pop("student_groups", [])
        student_parents = validated_data.pop("student_parents", [])
        student = super().create(validated_data)

        if student_groups:
            student.student_groups.set(student_groups)

        if student_parents:
            for parent in student_parents:
                parent.parent_students.add(student)

        return student
