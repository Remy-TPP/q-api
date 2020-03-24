from .models import *
from django.contrib.auth.models import User
from rest_framework import serializers

class UserSerializer(serializers.HyperlinkedModelSerializer):
    profile = serializers.HyperlinkedRelatedField(view_name="profile-detail", queryset=Profile.objects.all())

    class Meta:
        model = User
        fields = ['profile', 'username', 'first_name', 'last_name', 'email', 'is_active', 'date_joined']


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    usertypes = serializers.HyperlinkedRelatedField(many=True, view_name='usertype-detail', queryset=UserType.objects.all())
    groups = serializers.HyperlinkedRelatedField(many=True, view_name='group-detail', queryset=Group.objects.all())
    friends = serializers.HyperlinkedRelatedField(many=True, view_name='profile-detail', queryset=Profile.objects.all())

    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = '__all__'

class UserTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserType
        fields = '__all__'

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    users = serializers.HyperlinkedRelatedField(many=True, view_name='profile-detail', queryset=Profile.objects.all())

    class Meta:
        model = Group
        fields = '__all__'