from django.conf import settings

from rest_auth.serializers import PasswordResetSerializer
from rest_auth.models import TokenModel
from rest_framework.serializers import ModelSerializer
from apps.profiles.serializers import ProfileMinimalSerializer


class CustomPasswordResetSerializer(PasswordResetSerializer):
    def get_email_options(self):
        return {
            'email_template_name': 'reset_password_email.txt',
            'from_email': getattr(settings, 'EMAIL_HOST_USER'),
        }


class TokenSerializer(ModelSerializer):
    """
    Serializer for Token model.
    """
    profile = ProfileMinimalSerializer(source='user.profile')

    class Meta:
        model = TokenModel
        fields = ('key', 'profile')
