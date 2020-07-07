from rest_framework import viewsets, permissions

from apps.products.models import Unit, Product
from apps.products.serializers import UnitSerializer, ProductSerializer


class UnitViewSet(viewsets.ModelViewSet):
    """
    Manage units.

    Only Admin.

    list: Lists all units.

    Returns units.

    retrieve: Gets unit with id={id}.

    Returns unit.

    create: Creates unit.

    Returns unit.

    partial_update: Partial updates unit with id={id}.

    Returns unit.

    update: Updates unit with id={id}.

    Returns unit.

    delete: Deletes unit with id={id}.

    Returns none.
    """
    queryset = Unit.objects.all().order_by("id")
    serializer_class = UnitSerializer
    lookup_field = 'pk'
    permission_classes = [permissions.IsAdminUser]


class ProductViewSet(viewsets.ModelViewSet):
    """
    Manage products.

    Only Admin.

    list: Lists all products.

    Returns products.

    retrieve: Gets product with id={id}.

    Returns product.

    create: Creates product.

    Returns product.

    partial_update: Partial updates product with id={id}.

    Returns product.

    update: Updates product with id={id}.

    Returns product.

    delete: Deletes product with id={id}.

    Returns none.
    """
    queryset = Product.objects.all().order_by("id")
    serializer_class = ProductSerializer
    lookup_field = 'pk'
    permission_classes = [permissions.IsAdminUser]
