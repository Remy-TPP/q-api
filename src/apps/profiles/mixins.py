from django.contrib.auth.models import User

from apps.profiles.models import Profile, ProfileType, Group
from apps.profiles.serializers import ProfileSerializer, ProfileTypeSerializer, GroupSerializer, UserSerializer

class UserMixin(object):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class ProfileMixin(object):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

class ProfileTypeMixin(object):
    queryset = ProfileType.objects.all()
    serializer_class = ProfileTypeSerializer

class GroupMixin(object):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer