from .models import *
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    usertypes = serializers.HyperlinkedRelatedField(many=True, view_name='usertype-detail', queryset=UserType.objects.all())
    groups = serializers.HyperlinkedRelatedField(many=True, view_name='group-detail', queryset=Group.objects.all())
    
    class Meta:
        model = User
        fields = '__all__'

class UserTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserType
        fields = '__all__'

class GroupSerializer(serializers.ModelSerializer):
    users = serializers.HyperlinkedRelatedField(many=True, view_name='user-detail', queryset=User.objects.all())

    class Meta:
        model = Group
        fields = '__all__'