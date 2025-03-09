from rest_framework.viewsets import ModelViewSet
from django.contrib.auth import get_user_model

from .models import Parent, Student, Teacher, Group, Subject, Room, Admin, Superuser
from .serializers import ParentSerializer, StudentSerializer, TeacherSerializer, GroupSerializer, SubjectSerializer, \
    RoomSerializer, AdminSerializer, SuperuserSerializer

User = get_user_model()


class SuperuserViewSet(ModelViewSet):
    queryset = Superuser.objects.filter(is_active=True)
    serializer_class = SuperuserSerializer


class ParentViewSet(ModelViewSet):
    queryset = Parent.objects.filter(is_active=True)
    serializer_class = ParentSerializer


class StudentViewSet(ModelViewSet):
    queryset = Student.objects.filter(is_active=True)
    serializer_class = StudentSerializer


class TeacherViewSet(ModelViewSet):
    queryset = Teacher.objects.filter(is_active=True)
    serializer_class = TeacherSerializer


class GroupViewSet(ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class SubjectViewSet(ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


class RoomViewSet(ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer


class AdminViewSet(ModelViewSet):
    queryset = Admin.objects.filter(is_active=True)
    serializer_class = AdminSerializer
