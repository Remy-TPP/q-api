from rest_framework import viewsets

from django.contrib.auth.models import User
from apps.profiles.models import Profile, ProfileType, Group
from apps.profiles.serializers import ProfileSerializer, ProfileTypeSerializer, UserSerializer, GroupSerializer

from apps.profiles.permissions import UpdateDestroyOwnProfile

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("id")
    serializer_class = UserSerializer
    lookup_field='pk'

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all().order_by("id")
    serializer_class = ProfileSerializer
    lookup_field='pk'
    permission_classes=[UpdateDestroyOwnProfile]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ProfileTypeViewSet(viewsets.ModelViewSet):
    queryset = ProfileType.objects.all().order_by("id")
    serializer_class = ProfileTypeSerializer
    lookup_field='pk'

class GroupViewSet(viewsets.ModelViewSet):
    #permission_classes=[UpdateDestroyOwnProfile]
    queryset = Group.objects.all().order_by("id")
    serializer_class = GroupSerializer
    lookup_field='pk'


        