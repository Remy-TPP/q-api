from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q

from django.contrib.auth.models import User
from apps.profiles.models import Profile, ProfileType, Group, FriendshipRequest, FriendshipStatus
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

class FriendshipView(viewsets.GenericViewSet,
                     mixins.ListModelMixin,
                     mixins.CreateModelMixin):
    """
    list: List all friendship requests where current user is involved

    create: Create a friendship request from current user to user sent
    """
    queryset = FriendshipRequest.objects.all()
    serializer_class = FriendshipRequestSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return FriendshipRequest.objects.filter(
            Q(profile_requesting__user_id=self.request.user.id) |
            Q(profile_requested__user_id=self.request.user.id)
        )

    @action(detail=True, methods=['GET'])
    def accept(self, request, pk=None):
        """
        Accept the request with {id}

        Only if the status is REQUESTED and the profile_requested is the current user
        """
        friendship_request = get_object_or_404(FriendshipRequest.objects.all(), id=pk)

        if (friendship_request.status.name == 'REQUESTED' and
                friendship_request.profile_requested.user.id == request.user.id):
            friendship_request.status = FriendshipStatus.objects.get(name='ACCEPTED')
            friendship_request.profile_requested.friends.add(friendship_request.profile_requesting)
            friendship_request.save()
            return Response("Friend added!", status=status.HTTP_202_ACCEPTED)
        return Response("Cannot add friend!", status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['GET'])
    def reject(self, request, pk=None):
        """
        Delete the request with {id}

        Only if the status is REQUESTED.
        """
        friendship_request = get_object_or_404(FriendshipRequest.objects.all(), id=pk)

        if (friendship_request.status.name == 'REQUESTED'):
            friendship_request.status = FriendshipStatus.objects.get(name='REJECTED')
            friendship_request.save()
            return Response("Friendship Request deleted!", status=status.HTTP_200_OK)
        return Response("Cannot delete frienship request!", status=status.HTTP_400_BAD_REQUEST)


class ProfileTypeViewSet(viewsets.ModelViewSet):
    queryset = ProfileType.objects.all().order_by("id")
    serializer_class = ProfileTypeSerializer
    lookup_field = 'pk'

class GroupViewSet(viewsets.ModelViewSet):
    #permission_classes=[UpdateDestroyOwnProfile]
    queryset = Group.objects.all().order_by("id")
    serializer_class = GroupSerializer
    lookup_field = 'pk'
