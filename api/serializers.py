from rest_framework.serializers import ModelSerializer
from rest_framework import forms

from api.models import Superuser


class SuperuserSerializer(ModelSerializer):
    class Meta:
        model = Superuser
        fields = ['email', 'first_name', 'last_name', 'role', 'password', 'is_superuser', 'is_staff', 'is_active']
        extra_kwargs = {
            'password': {
                'style': {
                    'input_type': 'password',
                }
            }
        }
