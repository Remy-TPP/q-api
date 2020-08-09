from rest_framework import viewsets, status, mixins
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.db.transaction import atomic
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from apps.inventories.utils import get_place_or_default

from apps.inventories.models import (Place,
                                     Inventory,
                                     InventoryItem,
                                     PlaceMember)
from apps.inventories.serializers import (PlaceSerializer,
                                          InventorySerializer,
                                          InventoryItemSerializer)


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_summary="Lists all the places the user has.",
    operation_description="Returns places."
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_summary="Gets the place with id={id}..",
    operation_description="Returns place."
))
@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_summary="Creates a place for that user.",
    operation_description="Returns place."
))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    operation_summary="Partial updates place with id={id}.",
    operation_description="Returns place."
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    operation_summary="Updates place with id={id}.",
    operation_description="Returns place."
))
class PlaceViewSet(viewsets.GenericViewSet,
                   mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.ListModelMixin,
                   mixins.RetrieveModelMixin):
    queryset = Place.objects.all().order_by("id")
    serializer_class = PlaceSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        user = self.request.user
        return Place.objects.filter(members=user.profile).order_by("id")


class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all().order_by("id")
    serializer_class = InventorySerializer
    lookup_field = 'pk'


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_summary="Lists all items that place has.",
    operation_description="Returns items."
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_summary="Gets the item with id={id}..",
    operation_description="Returns item."
))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    operation_summary="Partial updates item with id={id}.",
    operation_description="Returns item."
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    operation_summary="Updates item with id={id}.",
    operation_description="Returns item."
))
@method_decorator(name='destroy', decorator=swagger_auto_schema(
    operation_summary="Deletes item with id={id}.",
    operation_description="Returns none."
))
class InventoryItemViewSet(viewsets.GenericViewSet,
                           mixins.CreateModelMixin,
                           mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin):
    queryset = InventoryItem.objects.all().order_by("id")
    serializer_class = InventoryItemSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return InventoryItem.objects.filter(inventory__place=self.kwargs['place_pk'])

    @swagger_auto_schema(
        operation_summary="Create an item for that place.",
        operation_description="Returns the item."
    )
    def create(self, request, *args, **kwargs):

        inventory = get_place_or_default(request.user.profile, kwargs['place_pk']).inventory

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(inventory=inventory)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            {
                'msg': "Cannot add Item!",
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


@swagger_auto_schema(
    method='post',
    operation_summary='Default place',
    operation_description='Choose a place you are member as a default place',
    manual_parameters=[
        openapi.Parameter(
            'place_id',
            in_=openapi.IN_QUERY,
            description='ID of a place',
            type=openapi.TYPE_INTEGER,
            required=True
        ),
    ]
)
@api_view(['POST'])
@atomic
def default_place(request):
    place_id = request.query_params.get('place_id')

    if place_id:
        PlaceMember.objects.filter(
            Q(member_id=request.user.profile) &
            Q(is_the_default_one=True)
        ).update(is_the_default_one=False)

        PlaceMember.objects.filter(
            Q(member_id=request.user.profile) &
            Q(place_id=place_id)
        ).update(is_the_default_one=True)
        return Response({'message': 'Your place has changed!'}, status=status.HTTP_200_OK)
    return Response({'message': 'place_id must be provided!'}, status=status.HTTP_400_BAD_REQUEST)
