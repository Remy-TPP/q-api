from rest_framework import serializers

from django.contrib.auth.models import User
from apps.profiles.models import (Profile,
                                  ProfileType,
                                  Event,
                                  FriendshipRequest,
                                  FriendshipStatus)


class UserSerializer(serializers.ModelSerializer):
    profile = serializers.HyperlinkedRelatedField(view_name="profile-detail", read_only=True)
    last_login = serializers.DateTimeField(read_only=True)

    class Meta:
        # TODO: should use `get_user_model()`?
        model = User
        exclude = ['user_permissions', 'groups', 'is_staff', 'is_superuser', 'password']


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    profiletypes = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='profiletype-detail',
        queryset=ProfileType.objects.all()
    )
    events = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='event-detail',
        read_only=True
    )
    friends = serializers.HyperlinkedRelatedField(
        many=True,
        view_name='profile-detail',
        read_only=True
    )

    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = '__all__'


class ProfileTypeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = ProfileType
        fields = '__all__'


class EventSerializer(serializers.ModelSerializer):
    host = serializers.StringRelatedField()
    attendees = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Profile.objects.all()
    )


    def create(self, validated_data):
        current_profile = self.context.get('request').user.profile
        place = validated_data.get('place')

        if place and not current_profile.places.filter(id=place.id).exists():
            raise serializers.ValidationError('Place is not valid!')

        friends_set = set(current_profile.friends.values_list('id', flat=True))
        attendees_set = set(attendee.id for attendee in validated_data.get('attendees'))

        if not attendees_set.issubset(friends_set):
            raise serializers.ValidationError('You can add only friends to an event!')

        validated_data['host'] = current_profile
        group = super(EventSerializer, self).create(validated_data)
        return group

    class Meta:
        model = Event
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
