from django.contrib.auth.models import User

from apps.profiles.models import Profile, ProfileType, Group
from apps.profiles.serializers import ProfileSerializer, ProfileTypeSerializer, GroupSerializer, UserSerializer

class UserMixin(object):
    queryset = User.objects.all().order_by("id")
    serializer_class = UserSerializer

class ProfileMixin(object):
    queryset = Profile.objects.all().order_by("id")
    serializer_class = ProfileSerializer

class ProfileTypeMixin(object):
    queryset = ProfileType.objects.all().order_by("id")
    serializer_class = ProfileTypeSerializer

class GroupMixin(object):
    queryset = Group.objects.all().order_by("id")
    serializer_class = GroupSerializer