from rest_framework import viewsets, status, mixins, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from apps.profiles.models import (Profile,
                                  ProfileType,
                                  Event,
                                  FriendshipRequest,
                                  FriendshipStatus,
                                  )
from apps.recipes.models import (Interaction)

from apps.profiles.serializers import (ProfileSerializer,
                                       ProfileMinimalSerializer,
                                       ProfileTypeSerializer,
                                       UserSerializer,
                                       EventSerializer,
                                       FriendshipRequestSerializer,
                                       FriendshipStatusSerializer,
                                       )
from apps.recipes.serializers import (InteractionSerializer)

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
    queryset = Profile.objects.all().order_by('id')
    serializer_class = ProfileSerializer
    lookup_field = 'pk'
    permission_classes = [UpdateOwnProfile, IsAuthenticated]
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'user__email']

    def list(self, request, *args, **kwargs):
        friendship_requests_sent = FriendshipRequest.objects.filter(
            Q(profile_requesting__user_id=self.request.user.id)
            & Q(status='REQUESTED')
            ).values_list('profile_requested_id', flat=True)

        friendship_requests_received = FriendshipRequest.objects.filter(
            Q(profile_requested__user_id=self.request.user.id)
            & Q(status='REQUESTED')
            ).values_list('profile_requesting_id', flat=True)

        queryset = self.filter_queryset(
            Profile.objects
            .exclude(id=self.request.user.profile.id)
            .exclude(id__in=self.request.user.profile.friends.values_list('id', flat=True))
            .exclude(id__in=friendship_requests_sent)
            .exclude(id__in=friendship_requests_received)
            .order_by('id')
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

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

    @swagger_auto_schema(
        method='get',
        operation_summary="Get a list of my friends.",
        responses={200: ProfileMinimalSerializer(many=True)}
    )
    @action(detail=False, methods=['GET'], url_path='friends')
    def my_friends(self, request):
        filtered_queryset = self.filter_queryset(request.user.profile.friends.all()).order_by('id')
        # TODO: maybe context={'request': request} is already included by default
        friends = ProfileMinimalSerializer(filtered_queryset, many=True, context={'request': request})
        return Response(friends.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        method='get',
        operation_summary="Get a list of recipes current user has cooked.",
        responses={200: InteractionSerializer(many=True)},
    )
    @action(detail=False, methods=['GET'], url_path='cooked_recipes', url_name='cooked-recipes')
    def cooked_recipes(self, request):
        queryset = (
            Interaction.objects
            .filter(profile=request.user.profile, cooked_at__len__gt=0)
        )
        queryset = sorted(queryset, key=lambda i: i.last_cooked, reverse=True)

        page = self.paginate_queryset(queryset)
        if page is not None:
            recipes_cooked_by_user = InteractionSerializer(page, many=True)
            return self.get_paginated_response(recipes_cooked_by_user.data)

        recipes_cooked_by_user = InteractionSerializer(queryset, many=True)
        return Response(recipes_cooked_by_user.data, status=status.HTTP_200_OK)


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
            (Q(profile_requesting__user_id=self.request.user.id) |
             Q(profile_requested__user_id=self.request.user.id)) &
            Q(status='REQUESTED')
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
    search_fields = ['name']


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
    search_fields = ['name', 'place__name']

    def get_queryset(self):
        profile = self.request.user.profile
        return self.filter_queryset(Event.objects.filter(
            Q(host=profile) |
            Q(attendees=profile)
        ).order_by("id").distinct())

    @swagger_auto_schema(
        method='post',
        operation_summary="Add an attendee to the event.",
        manual_parameters=[
            openapi.Parameter(
                'attendee_id',
                in_=openapi.IN_QUERY,
                description='ID of an attendee',
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ]
    )
    @action(detail=True, methods=['POST'])
    def add_attendee(self, request, pk=None):
        attendee_id = request.query_params.get('attendee_id')
        if not attendee_id:
            return Response({"error": "Must provide attendee_id!"}, status=status.HTTP_400_BAD_REQUEST)

        attendee = get_object_or_404(request.user.profile.friends.all(), id=attendee_id)
        event = get_object_or_404(Event.objects.all(), id=pk)

        event.attendees.add(attendee)

        return Response({"msg": "Attendee has been added!"}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        method='post',
        operation_summary="Remove an attendee from the event.",
        manual_parameters=[
            openapi.Parameter(
                'attendee_id',
                in_=openapi.IN_QUERY,
                description='ID of an attendee',
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ]
    )
    @action(detail=True, methods=['POST'])
    def remove_attendee(self, request, pk=None):
        attendee_id = request.query_params.get('attendee_id')
        if not attendee_id:
            return Response({"error": "Must provide attendee_id!"}, status=status.HTTP_400_BAD_REQUEST)

        event = get_object_or_404(Event.objects.all(), id=pk)

        event.attendees.remove(attendee_id)

        return Response({"msg": "Attendee has been deleted!"}, status=status.HTTP_200_OK)


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
    queryset = FriendshipStatus.objects.all().order_by("pk")
    serializer_class = FriendshipStatusSerializer
    lookup_field = 'pk'
    permission_classes = [permissions.IsAdminUser]
