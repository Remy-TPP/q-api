from django.conf import settings

from rest_auth.serializers import PasswordResetSerializer


class CustomPasswordResetSerializer(PasswordResetSerializer):
    def get_email_options(self):
        return {
            'email_template_name': 'reset_password_email.txt',
            'from_email': getattr(settings, 'EMAIL_HOST_USER'),
        }
