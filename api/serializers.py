from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from api.models import Superuser


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['email'] = user.name
        token['first_name'] = user.name
        token['last_name'] = user.name
        token['role'] = user.name
        token['is_superuser'] = user.name
        token['is_staff'] = user.name

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
