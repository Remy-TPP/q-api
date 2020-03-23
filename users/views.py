from rest_framework import generics
from .models import User
from .serializers import UserSerializer
from django.shortcuts import get_object_or_404

class Users(generics.ListCreateAPIView):
	queryset = User.objects.all()
	serializer_class = UserSerializer

class User(generics.RetrieveUpdateDestroyAPIView):
	queryset = User.objects.all()
	serializer_class = UserSerializer
	lookup_field='pk'

