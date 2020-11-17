from rest_framework import serializers
from django.contrib.auth import get_user_model

from apps.profiles.fields import (EventField,
                                  AttendeeField)
from apps.profiles.models import (Profile,
                                  ProfileType,
                                  Event,
                                  FriendshipRequest,
                                  FriendshipStatus,
                                  RecipeCooked)


class UserSerializer(serializers.ModelSerializer):
    last_login = serializers.DateTimeField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = get_user_model()
        exclude = ['user_permissions', 'groups', 'is_staff', 'is_superuser', 'password']


class ProfileMinimalSerializer(serializers.ModelSerializer):
    username = serializers.StringRelatedField(source='user.username')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.EmailField(read_only=True, source='user.email')

    class Meta:
        model = Profile
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class ProfileSerializer(serializers.ModelSerializer):
    profiletypes = serializers.SlugRelatedField(
        slug_field="name",
        many=True,
        queryset=ProfileType.objects.all()
    )
    events = EventField(
        many=True,
        view_name='event-detail',
        read_only=True
    )
    friends = serializers.StringRelatedField(
        many=True,
        read_only=True
    )

    last_login = serializers.DateTimeField(read_only=True, source='user.last_login')
    is_active = serializers.BooleanField(read_only=True, source='user.is_active')
    username = serializers.StringRelatedField(source='user.username')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.EmailField(read_only=True, source='user.email')
    date_joined = serializers.DateTimeField(read_only=True, source='user.date_joined')

    class Meta:
        model = Profile
        exclude = ['user', 'recipes_cooked']

    def update(self, instance, validated_data):
        user = validated_data.pop('user', None)

        if (user):
            instance.user.first_name = user.get('first_name', instance.user.first_name)
            instance.user.last_name = user.get('last_name', instance.user.last_name)

            instance.user.save()

        return super(ProfileSerializer, self).update(instance, validated_data)


class RecipeCookedSerializer(serializers.ModelSerializer):
    score = serializers.IntegerField(min_value=1, max_value=10, required=False)
    profile = serializers.StringRelatedField()
    recipe = serializers.StringRelatedField()
    cooked_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = RecipeCooked
        fields = '__all__'
        read_only_fields = ['id']


class ProfileTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProfileType
        fields = '__all__'


class EventSerializer(serializers.ModelSerializer):
    host = serializers.StringRelatedField()
    attendees_id = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Profile.objects.all(),
        source="attendees",
        write_only=True
    )
    attendees = AttendeeField(
        many=True,
        read_only=True
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
    profile_requesting = ProfileMinimalSerializer(
        read_only=True
    )
    profile_requested = ProfileMinimalSerializer(
        read_only=True
    )
    profile_requested_id = serializers.PrimaryKeyRelatedField(
        queryset=Profile.objects.all(),
        write_only=True
    )

    def create(self, validated_data):
        current_profile = Profile.objects.get(user=self.context['request'].user)
        requested_profile = validated_data['profile_requested_id']
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
