from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from django.utils import timezone

from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField, HyperlinkedIdentityField
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Student, Group, Subject, Parent, Room, Teacher, Admin, Superuser

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
        Create user instance with hashed password
        """
        password = validated_data.pop("password", None)
        user = self.Meta.model.objects.create_user(**validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        if password:
            instance.set_password(password)
            instance.save()

        return super().update(instance, validated_data)


class UserSerializer(PasswordHashMixin, ModelSerializer):
    """
    Base User serializer
    """

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "middle_name", "phone_number", "role", "password", "created", "updated"]
        extra_kwargs = {
            "password": {
                "write_only": True,
            },
            "role": {
                "read_only": True
            }
        }


class SuperuserSerializer(UserSerializer):
    """
    Serializer for Superuser model
    """
    class Meta(UserSerializer.Meta):
        model = Superuser


class AdminSerializer(UserSerializer):
    """
    Serializer for Admin model with password hashing and field exclusion.
    """
    class Meta(UserSerializer.Meta):
        model = Admin


class SubjectSerializer(ModelSerializer):
    """
    Serializer for Subject model
    """

    class Meta:
        model = Subject
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["groups"] = Group.objects.filter(subject=instance).count()
        return representation
    

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
        fields = ["id", "email", "first_name", "last_name", "middle_name", "phone_number", "role", "created", "updated"]


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


class TeacherSerializer(UserSerializer):
    """
    Serializer for Teacher model
    """

    class Meta(UserSerializer.Meta):
        model = Teacher


class GroupSerializer(ModelSerializer):
    """
    Serializer for Group model with subject and teacher nested representations
    """

    subject = PrimaryKeyRelatedField(queryset=Subject.objects.all(), many=False, required=True)
    teacher = PrimaryKeyRelatedField(queryset=Teacher.objects.all(), many=False, required=True)

    class Meta:
        model = Group
        fields = "__all__"
        extra_kwargs = {
            "is_active": {
                "read_only": True,
            }
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["subject"] = SubjectSerializer(instance.subject, many=False).data
        representation["teacher"] = TeacherSerializer(instance.teacher, many=False).data
        return representation

    def update_group_status(self, validated_data):
        """
        Custom method to update group's active status on each create/update
        """
        start_date = validated_data.get("start_date")
        if start_date and start_date <= timezone.now().date():
            validated_data["is_active"] = True
        else:
            validated_data["is_active"] = False
        return validated_data


    def create(self, validated_data):
        validated_data = self.update_group_status(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data = self.update_group_status(validated_data)
        return super().update(instance, validated_data)


class StudentSerializer(UserSerializer):
    """
    Serializer for Student model with password hashing and nested relationships for groups and parents
    """
    student_groups = PrimaryKeyRelatedField(queryset=Group.objects.all(), many=True, required=False)
    student_parents = PrimaryKeyRelatedField(queryset=Parent.objects.all(), many=True, required=False)

    class Meta(UserSerializer.Meta):
        model = Student
        fields = UserSerializer.Meta.fields + ["student_groups", "student_parents"]

    def to_representation(self, instance):
        """
        Add nested group and parent data to the serialized representation.
        """
        representation = super().to_representation(instance)
        representation["student_groups"] = GroupSerializer(instance.student_groups.all(), many=True,
                                                           context=self.context).data
        representation["student_parents"] = StudentParentSerializer(instance.parents.all(), many=True,
                                                            context=self.context).data
        representation["is_preferential"] = "true" if instance.is_preferential else "false"
        representation["preferential_amount"] = instance.preferential_amount if instance.is_preferential else 0
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
