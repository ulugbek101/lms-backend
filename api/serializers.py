from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from api.models import Superuser


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['role'] = user.get_role_name
        token['is_superuser'] = user.is_superuser
        token['is_staff'] = user.is_staff

        return token


class StaffSerializer(ModelSerializer):
    class Meta:
        model = Superuser
        fields = ['email', 'first_name', 'last_name', 'role', 'password', 'is_superuser', 'is_staff']
        extra_kwargs = {
            'password': {
                'style': {
                    'input_type': 'password',
                }
            }
        }
