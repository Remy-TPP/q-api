from rest_framework import generics
from django.contrib.auth.models import User

from apps.profiles.serializers import *
from apps.profiles.permissions import *
from apps.profiles.mixins import *

class UsersView(UserMixin, generics.ListCreateAPIView):
    pass

class UserView(UserMixin, generics.RetrieveUpdateDestroyAPIView):
    lookup_field='pk'

class ProfilesView(ProfileMixin, generics.ListCreateAPIView):
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ProfileView(ProfileMixin, generics.RetrieveUpdateDestroyAPIView):
    permission_classes=[UpdateDestroyOwnProfile]

    lookup_field='pk'
        
class profiletypesView(ProfileTypeMixin, generics.ListCreateAPIView):
    pass

class ProfileTypeView(ProfileTypeMixin, generics.RetrieveUpdateDestroyAPIView):
    lookup_field='pk'

class GroupsView(GroupMixin, generics.ListCreateAPIView):
    pass

class GroupView(GroupMixin, generics.RetrieveUpdateDestroyAPIView):
    #permission_classes=[UpdateDestroyOwnProfile]

    lookup_field='pk'


        