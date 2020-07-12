from rest_framework import viewsets, status, mixins, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from apps.inventories.models import (Place,
                                     Inventory,
                                     InventoryItem)
from apps.inventories.serializers import (PlaceSerializer,
                                          InventorySerializer,
                                          InventoryItemSerializer)

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

    def create(self, request, *args, **kwargs):
        inventory = get_object_or_404(Place.objects.all(), id=kwargs['place_pk']).inventory

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
