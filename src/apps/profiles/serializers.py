from rest_framework import serializers

from django.contrib.auth.models import User
from apps.profiles.models import (Profile,
                                  ProfileType,
                                  Group,
                                  FriendshipRequest,
                                  FriendshipStatus)

class UserSerializer(serializers.ModelSerializer):
    profile = serializers.HyperlinkedRelatedField(view_name="profile-detail", read_only=True)
    last_login = serializers.DateTimeField(read_only=True)

    class Meta:
        model = User
        exclude = ['user_permissions', 'groups', 'is_staff', 'is_superuser', 'password']


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    profiletypes = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='profiletype-detail',
        queryset=ProfileType.objects.all()
    )
    groups = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='group-detail',
        queryset=Group.objects.all()
    )
    friends = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='profile-detail',
        queryset=Profile.objects.all()
    )

    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = '__all__'

class ProfileTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ProfileType
        fields = '__all__'

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.HyperlinkedRelatedField(view_name='profile-detail', read_only=True)

    def create(self, validated_data):
        current_profile = Profile.objects.get(user=self.context['request'].user)

        members = validated_data.pop('members') if 'members' in validated_data else []
        members.append(current_profile)

        group = Group.objects.create(owner=current_profile)

        group.members.set(members)

        return group

    class Meta:
        model = Group
        fields = '__all__'

class FriendshipRequestSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)
    profile_requesting = serializers.PrimaryKeyRelatedField(
        read_only=True
    )
    profile_requested = serializers.PrimaryKeyRelatedField(
        queryset=Profile.objects.all()
    )

    def create(self, validated_data):
        current_profile = Profile.objects.get(user=self.context['request'].user)
        requested_profile = validated_data['profile_requested']
        requested_status = FriendshipStatus.objects.get(name='REQUESTED')

        friendship_request, created = FriendshipRequest.objects.get_or_create(
            profile_requested=requested_profile,
            profile_requesting=current_profile,
            defaults={'status': requested_status}
        )

        if not created:
            friendship_request.status = requested_status
            friendship_request.save()

        return friendship_request

    class Meta:
        model = FriendshipRequest
        fields = '__all__'

class FriendshipStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = FriendshipStatus
        fields = '__all__'
