from rest_framework import viewsets, status, mixins, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema

from apps.profiles.models import (Profile,
                                  ProfileType,
                                  Event,
                                  FriendshipRequest,
                                  FriendshipStatus)

from apps.profiles.serializers import (ProfileSerializer,
                                       ProfileTypeSerializer,
                                       UserSerializer,
                                       EventSerializer,
                                       FriendshipRequestSerializer,
                                       FriendshipStatusSerializer)

from apps.profiles.permissions import (UpdateOwnProfile,
                                       IsOwnProfile)


class UserViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all().order_by("id")
    serializer_class = UserSerializer
    lookup_field = 'pk'


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_summary="Lists all profiles.",
    operation_description="Returns profiles."
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_summary="Gets profile with id={id}.",
    operation_description="Returns profile."
))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    operation_summary="Partial updates profile with id={id}",
    operation_description="Returns profile. Only own profile."
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    operation_summary="Updates profile with id={id}.",
    operation_description="Returns profile. Only own profile."
))
class ProfileViewSet(viewsets.GenericViewSet,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin):
    queryset = Profile.objects.all().order_by("id")
    serializer_class = ProfileSerializer
    lookup_field = 'pk'
    permission_classes = [UpdateOwnProfile]
    search_fields = ['biography']

    @swagger_auto_schema(
        method='post',
        operation_summary="Set profile's user is_active to False.",
        operation_description="Only if the user of this profile is active"
    )
    @action(detail=True, methods=['POST'], permission_classes=[IsOwnProfile])
    def inactivate(self, request, pk=None):
        profile = get_object_or_404(Profile.objects.all(), id=pk)

        self.check_object_permissions(self.request, profile)

        if profile.user.is_active:
            profile.user.is_active = False
            profile.user.save()
            serializer = self.get_serializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response("The user is already inactive!", status=status.HTTP_400_BAD_REQUEST)


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_summary="List all friendship requests.",
    operation_description="Only where current user is involved."
))
@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_summary="Create a friendship request.",
    operation_description="From current user to user sent."
))
class FriendshipRequestViewSet(viewsets.GenericViewSet,
                               mixins.ListModelMixin,
                               mixins.CreateModelMixin):
    queryset = FriendshipRequest.objects.all().order_by('id')
    serializer_class = FriendshipRequestSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return FriendshipRequest.objects.filter(
            Q(profile_requesting__user_id=self.request.user.id) |
            Q(profile_requested__user_id=self.request.user.id)
        ).order_by("id")

    @swagger_auto_schema(
        method='post',
        operation_summary="Accept the request with {id}.",
        operation_description="Only if the status is REQUESTED and the profile_requested is the current user."
    )
    @action(detail=True, methods=['POST'])
    def accept(self, request, pk=None):
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

    @swagger_auto_schema(
        method='post',
        operation_summary="Delete the request with {id}.",
        operation_description="Only if the status is REQUESTED."
    )
    @action(detail=True, methods=['POST'])
    def reject(self, request, pk=None):
        friendship_request = get_object_or_404(FriendshipRequest.objects.all(), id=pk)
        status_requested = get_object_or_404(FriendshipStatus, name='REQUESTED')
        status_rejected = get_object_or_404(FriendshipStatus, name='REJECTED')

        if friendship_request.status == status_requested:
            friendship_request.status = status_rejected
            friendship_request.save()
            serializer = self.get_serializer(friendship_request)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response("Cannot delete friendship request!", status=status.HTTP_400_BAD_REQUEST)


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_summary="Lists all profiletypes.",
    operation_description="Returns profiletypes."
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_summary="Gets profiletype with id={id}..",
    operation_description="Returns profiletype."
))
@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_summary="Creates profiletype.",
    operation_description="Returns profiletype."
))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    operation_summary="Partial updates profiletype with id={id}.",
    operation_description="Returns profiletype."
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    operation_summary="Updates profiletype with id={id}.",
    operation_description="Returns profiletype."
))
@method_decorator(name='destroy', decorator=swagger_auto_schema(
    operation_summary="Deletes profiletype with id={id}.",
    operation_description="Returns none."
))
class ProfileTypeViewSet(viewsets.ModelViewSet):
    """
    Manage the types of profiles. (Vegan, Celiac, etc.).

    Only Admin.
    """
    queryset = ProfileType.objects.all().order_by("id")
    serializer_class = ProfileTypeSerializer
    lookup_field = 'pk'
    permission_classes = [permissions.IsAdminUser]


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_summary="Lists all events.",
    operation_description="Returns groups."
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_summary="Gets event with id={id}..",
    operation_description="Returns group."
))
@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_summary="Creates event.",
    operation_description="Returns group."
))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    operation_summary="Partial updates event with id={id}.",
    operation_description="Returns group."
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    operation_summary="Updates event with id={id}.",
    operation_description="Returns group."
))
@method_decorator(name='destroy', decorator=swagger_auto_schema(
    operation_summary="Deletes event with id={id}.",
    operation_description="Returns none."
))
class EventViewSet(viewsets.ModelViewSet):
    """
    Manage the groups of profiles.
    """
    queryset = Event.objects.all().order_by("id")
    serializer_class = EventSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        profile = self.request.user.profile
        return Event.objects.filter(
            Q(host=profile) |
            Q(attendees=profile)
        ).order_by("id").distinct()


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_summary="Lists all friendshipstatus.",
    operation_description="Returns friendshipstatus."
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_summary="Gets friendshipstatus with id={id}..",
    operation_description="Returns friendshipstatus."
))
@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_summary="Creates friendshipstatus.",
    operation_description="Returns friendshipstatus."
))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    operation_summary="Partial updates friendshipstatus with id={id}.",
    operation_description="Returns friendshipstatus."
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    operation_summary="Updates friendshipstatus with id={id}.",
    operation_description="Returns friendshipstatus."
))
@method_decorator(name='destroy', decorator=swagger_auto_schema(
    operation_summary="Deletes friendshipstatus with id={id}.",
    operation_description="Returns none."
))
class FriendshipStatusViewSet(viewsets.ModelViewSet):
    """
    Manage the friendshipstatus of profiles.

    Only Admin.
    """
    queryset = FriendshipStatus.objects.all().order_by("id")
    serializer_class = FriendshipStatusSerializer
    lookup_field = 'pk'
    permission_classes = [permissions.IsAdminUser]
