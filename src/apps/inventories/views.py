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

class InventoryItemViewSet(viewsets.GenericViewSet):
    queryset = InventoryItem.objects.all().order_by("id")
    serializer_class = InventoryItemSerializer
    lookup_field = 'pk'

    @action(detail=True, methods=['POST'])
    def add_item(self, request, pk=None):
        breakpoint()
        inventory = get_object_or_404(Place.objects.all(), id=pk).inventory

        serializer = InventoryItemSerializer(data=request.data)
        #TODO: solo tiene que enviar product y amount, ver el model y sino el serializer para cambiar
        if serializer.is_valid():
            #TODO: crear el item y agregarlo al inventario
            item = InventoryItem.objects.create(serializer.data)
            inventory.items.add(item)
            return Response(inventory, status=status.HTTP_201_CREATED)
        return Response(
            {
                'msg': "Cannot add Item!",
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
