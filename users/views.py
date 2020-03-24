from rest_framework import generics
from .models import *
from django.contrib.auth.models import User
from .serializers import *
from django.shortcuts import get_object_or_404
from .permissions import *

class Users(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class User(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field='pk'

class Profiles(generics.ListCreateAPIView):

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class Profile(generics.RetrieveUpdateDestroyAPIView):
    permission_classes=[UpdateDestroyOwnProfile]
    
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    lookup_field='pk'
        

class UserTypes(generics.ListCreateAPIView):
    queryset = UserType.objects.all()
    serializer_class = UserTypeSerializer

class UserType(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserType.objects.all()
    serializer_class = UserTypeSerializer
    lookup_field='pk'

class Groups(generics.ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class Group(generics.RetrieveUpdateDestroyAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    lookup_field='pk'