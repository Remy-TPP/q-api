from rest_framework import serializers
from django.db.models import Q

from django.contrib.auth.models import User
from apps.profiles.models import Profile, ProfileType, Group, FriendshipRequest, FriendshipStatus

class UserSerializer(serializers.ModelSerializer):
    profile = serializers.HyperlinkedRelatedField(view_name="profile-detail", read_only=True)
    last_login = serializers.DateTimeField(read_only=True)

    class Meta:
        model = User
        exclude = ['user_permissions', 'groups', 'is_staff', 'is_superuser', 'password']


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    profiletypes = serializers.HyperlinkedRelatedField(many=True, view_name='profiletype-detail', queryset=ProfileType.objects.all())
    groups = serializers.HyperlinkedRelatedField(many=True, view_name='group-detail', queryset=Group.objects.all())
    friends = serializers.HyperlinkedRelatedField(many=True, view_name='profile-detail', queryset=Profile.objects.all())

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
    profile_requesting = serializers.HyperlinkedRelatedField(view_name="profile-detail", read_only=True)
    profile_requested = serializers.HyperlinkedRelatedField(view_name="profile-detail", queryset=Profile.objects.all())

    def create(self, validated_data):
        current_profile = Profile.objects.get(user=self.context['request'].user)
        requested_profile = validated_data['profile_requested']

        if not (FriendshipRequest.objects.filter(
                Q(profile_requesting=current_profile), 
                Q(profile_requested=requested_profile))):
            
            requested_status = FriendshipStatus.objects.get(name='REQUESTED')

            return FriendshipRequest.objects.create(
                profile_requested=requested_profile,
                profile_requesting=current_profile,
                status=requested_status
            )

        raise TypeError('Friendship request cannot be created!')

    class Meta:
        model = FriendshipRequest
        fields = '__all__'

