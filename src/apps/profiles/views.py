from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins
from django.shortcuts import get_object_or_404

from django.contrib.auth.models import User
from apps.profiles.models import Profile, ProfileType, Group, FriendshipRequest
from apps.profiles.serializers import (ProfileSerializer,
                                    ProfileTypeSerializer,
                                    UserSerializer,
                                    GroupSerializer,
                                    FriendshipRequestSerializer)

from apps.profiles.permissions import UpdateDestroyOwnProfile

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("id")
    serializer_class = UserSerializer
    lookup_field = 'pk'

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all().order_by("id")
    serializer_class = ProfileSerializer
    lookup_field = 'pk'
    permission_classes = [UpdateDestroyOwnProfile]

    # @action(detail=True, methods=['POST'], url_path='add_friend/(?P<friend_pk>[^/.]+)')
    # def add_friend(self, request, friend_pk, pk=None):
    #     queryset = Profile.objects.all()
    #     friend = get_object_or_404(queryset, pk=friend_pk)
    #     me = get_object_or_404(queryset, pk=pk)
    #     breakpoint()
    #     me.friends.add(friend)
    #     return Response("ok")

class FriendshipView(viewsets.ModelViewSet):
    queryset = FriendshipRequest.objects.all()
    serializer_class = FriendshipRequestSerializer
    lookup_field = 'profile_requested_id'

    def get_queryset(self):
        return FriendshipRequest.objects.filter(profile_requesting__user_id=self.request.user.id)

class ProfileTypeViewSet(viewsets.ModelViewSet):
    queryset = ProfileType.objects.all().order_by("id")
    serializer_class = ProfileTypeSerializer
    lookup_field = 'pk'

class GroupViewSet(viewsets.ModelViewSet):
    #permission_classes=[UpdateDestroyOwnProfile]
    queryset = Group.objects.all().order_by("id")
    serializer_class = GroupSerializer
    lookup_field = 'pk'

