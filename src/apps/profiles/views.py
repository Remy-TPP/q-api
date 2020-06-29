from rest_framework import viewsets, status, mixins, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q

from django.contrib.auth.models import User
from apps.profiles.models import (Profile,
                                  ProfileType,
                                  Group,
                                  FriendshipRequest,
                                  FriendshipStatus)

from apps.profiles.serializers import (ProfileSerializer,
                                       ProfileTypeSerializer,
                                       UserSerializer,
                                       GroupSerializer,
                                       FriendshipRequestSerializer,
                                       FriendshipStatusSerializer)

from apps.profiles.permissions import (UpdateOwnProfile,
                                       IsOwnProfile)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("id")
    serializer_class = UserSerializer
    lookup_field = 'pk'


class ProfileViewSet(viewsets.GenericViewSet,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin):
    """
    Manage profiles

    list: Lists all profiles.

    Returns profiles.

    retrieve: Gets profile with id={id}.

    Returns profile.

    partial_update: Partial updates profile with id={id}.

    Returns profile. Only own profile.

    update: Updates profile with id={id}.

    Returns profile. Only own profile.
    """
    queryset = Profile.objects.all().order_by("id")
    serializer_class = ProfileSerializer
    lookup_field = 'pk'
    permission_classes = [UpdateOwnProfile]

    @action(detail=True, methods=['POST'], permission_classes=[IsOwnProfile])
    def inactivate(self, request, pk=None):
        """
        Set profile's user is_active to False.

        Only if the user of this profile is active
        """
        profile = get_object_or_404(Profile.objects.all(), id=pk)

        self.check_object_permissions(self.request, profile)

        if profile.user.is_active:
            profile.user.is_active = False
            profile.user.save()
            serializer = self.get_serializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response("The user is already inactive!", status=status.HTTP_400_BAD_REQUEST)


class FriendshipRequestViewSet(viewsets.GenericViewSet,
                               mixins.ListModelMixin,
                               mixins.CreateModelMixin):
    """
    list: List all friendship requests.

    Only where current user is involved.

    create: Create a friendship request.

    From current user to user sent.
    """
    queryset = FriendshipRequest.objects.all().order_by('id')
    serializer_class = FriendshipRequestSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return FriendshipRequest.objects.filter(
            Q(profile_requesting__user_id=self.request.user.id) |
            Q(profile_requested__user_id=self.request.user.id)
        ).order_by("id")

    @action(detail=True, methods=['POST'])
    def accept(self, request, pk=None):
        """
        Accept the request with {id}.

        Only if the status is REQUESTED and the profile_requested is the current user.
        """
        friendship_request = get_object_or_404(FriendshipRequest.objects.all(), id=pk)
        status_requested = get_object_or_404(FriendshipStatus, name='REQUESTED')
        status_accepted = get_object_or_404(FriendshipStatus, name='ACCEPTED')

        if (friendship_request.status == status_requested and
                friendship_request.profile_requested.user.id == request.user.id):
            friendship_request.status = status_accepted
            friendship_request.profile_requested.friends.add(friendship_request.profile_requesting)
            friendship_request.save()
            serializer = self.get_serializer(friendship_request)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response("Cannot add friend!", status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST'])
    def reject(self, request, pk=None):
        """
        Delete the request with {id}.

        Only if the status is REQUESTED.
        """
        friendship_request = get_object_or_404(FriendshipRequest.objects.all(), id=pk)
        status_requested = get_object_or_404(FriendshipStatus, name='REQUESTED')
        status_rejected = get_object_or_404(FriendshipStatus, name='REJECTED')

        if friendship_request.status == status_requested:
            friendship_request.status = status_rejected
            friendship_request.save()
            serializer = self.get_serializer(friendship_request)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response("Cannot delete frienship request!", status=status.HTTP_400_BAD_REQUEST)


class ProfileTypeViewSet(viewsets.ModelViewSet):
    """
    Manage the types of profiles. (Vegan, Celiac, etc.).

    Only Admin.

    list: Lists all profiletypes.

    Returns profiletypes.

    retrieve: Gets profiletype with id={id}.

    Returns profiletype.

    create: Creates profiletype.

    Returns profiletype.

    partial_update: Partial updates profiletype with id={id}.

    Returns profiletype.

    update: Updates profiletype with id={id}.

    Returns profiletype.

    delete: Deletes profiletype with id={id}.

    Returns none.
    """
    queryset = ProfileType.objects.all().order_by("id")
    serializer_class = ProfileTypeSerializer
    lookup_field = 'pk'
    permission_classes = [permissions.IsAdminUser]


class GroupViewSet(viewsets.ModelViewSet):
    """
    Manage the groups of profiles.

    list: Lists all groups.

    Returns groups.

    retrieve: Gets group with id={id}.

    Returns group.

    create: Creates group.

    Returns group.

    partial_update: Partial updates group with id={id}.

    Returns group.

    update: Updates group with id={id}.

    Returns group.

    delete: Deletes group with id={id}.

    Returns none.
    """
    queryset = Group.objects.all().order_by("id")
    serializer_class = GroupSerializer
    lookup_field = 'pk'


class FriendshipStatusViewSet(viewsets.ModelViewSet):
    """
    Manage the frienshipstatus of profiles.

    Only Admin.

    list: Lists all frienshipstatus.

    Returns frienshipstatus.

    retrieve: Gets frienshipstatus with id={id}.

    Returns frienshipstatus.

    create: Creates frienshipstatus.

    Returns frienshipstatus.

    partial_update: Partial updates frienshipstatus with id={id}.

    Returns frienshipstatus.

    update: Updates frienshipstatus with id={id}.

    Returns frienshipstatus.

    delete: Deletes frienshipstatus with id={id}.

    Returns none.
    """
    queryset = FriendshipStatus.objects.all().order_by("id")
    serializer_class = FriendshipStatusSerializer
    lookup_field = 'pk'
    permission_classes = [permissions.IsAdminUser]
