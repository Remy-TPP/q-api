from rest_framework import viewsets, status, mixins, permissions

from apps.inventories.models import (Place,
                                     Inventory)
from apps.inventories.serializers import (PlaceSerializer,
                                          InventorySerializer)

class PlaceViewSet(viewsets.GenericViewSet,
                   mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.ListModelMixin,
                   mixins.RetrieveModelMixin):
    queryset = Place.objects.all().order_by("id")
    serializer_class = PlaceSerializer
    lookup_field = 'pk'


class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all().order_by("id")
    serializer_class = InventorySerializer
    lookup_field = 'pk'
