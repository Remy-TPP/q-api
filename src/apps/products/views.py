from rest_framework import viewsets, permissions
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema

from common.permissions import ReadOnly
from apps.products.models import Unit, Product
from apps.products.serializers import UnitSerializer, ProductSerializer


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_summary="Lists all units.",
    operation_description="Returns units."
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_summary="Gets unit with id={id}.",
    operation_description="Returns unit."
))
@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_summary="Creates unit.",
    operation_description="Returns unit."
))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    operation_summary="Partial updates unit with id={id}.",
    operation_description="Returns unit."
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    operation_summary="Updates unit with id={id}.",
    operation_description="Returns unit."
))
@method_decorator(name='destroy', decorator=swagger_auto_schema(
    operation_summary="Deletes unit with id={id}.",
    operation_description="Returns none."
))
class UnitViewSet(viewsets.ModelViewSet):
    """
    Manage units.

    Only Admin or read-only.
    """
    queryset = Unit.objects.all().order_by("id")
    serializer_class = UnitSerializer
    lookup_field = 'pk'
    permission_classes = [permissions.IsAdminUser | ReadOnly]
    search_fields = ['name', 'short_name', 'dimensionality']


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_summary="Lists all products.",
    operation_description="Returns products."
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_summary="Gets product with id={id}.",
    operation_description="Returns product."
))
@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_summary="Creates product.",
    operation_description="Returns product."
))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    operation_summary="Partial updates product with id={id}.",
    operation_description="Returns product."
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    operation_summary="Updates product with id={id}.",
    operation_description="Returns product."
))
@method_decorator(name='destroy', decorator=swagger_auto_schema(
    operation_summary="Deletes product with id={id}.",
    operation_description="Returns none."
))
class ProductViewSet(viewsets.ModelViewSet):
    """
    Manage products.

    Only Admin or read-only.
    """
    queryset = Product.objects.all().order_by("id")
    serializer_class = ProductSerializer
    lookup_field = 'pk'
    permission_classes = [permissions.IsAdminUser | ReadOnly]
    search_fields = ['name']
