from django.contrib.auth.models import User

from apps.users.models import *
from apps.users.serializers import *

class UserMixin(object):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class ProfileMixin(object):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

class UserTypeMixin(object):
    queryset = UserType.objects.all()
    serializer_class = UserTypeSerializer

class GroupMixin(object):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer