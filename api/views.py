from rest_framework.viewsets import ModelViewSet
from django.contrib.auth import get_user_model

from .serializers import StaffSerializer

User = get_user_model()


class StaffViewSet(ModelViewSet):
    queryset = User.objects.filter(is_active=True)
    serializer_class = StaffSerializer
