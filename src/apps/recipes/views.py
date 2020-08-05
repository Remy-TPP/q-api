from rest_framework import viewsets, permissions
from rest_framework.parsers import FileUploadParser
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema

# from apps.recipes.models import DishCategory, DishLabel, Dish, Ingredient, Recipe
from apps.recipes.models import DishCategory, DishLabel, Dish, Recipe
# from apps.recipes.serializers import (DishCategorySerializer, DishLabelSerializer, DishSerializer,
#                                       IngredientSerializer, RecipeSerializer)
from apps.recipes.serializers import DishCategorySerializer, DishLabelSerializer, DishSerializer, RecipeSerializer
from apps.recipes.permissions import ReadOnly


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_summary="Lists all dish categories.",
    operation_description="Returns dish categories."
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_summary="Gets dish category with id={id}.",
    operation_description="Returns dish category."
))
@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_summary="Creates dish category.",
    operation_description="Returns dish category."
))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    operation_summary="Partial updates dish category with id={id}.",
    operation_description="Returns dish category."
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    operation_summary="Updates dish category with id={id}.",
    operation_description="Returns dish category."
))
@method_decorator(name='destroy', decorator=swagger_auto_schema(
    operation_summary="Deletes dish category with id={id}.",
    operation_description="Returns none."
))
class DishCategoryViewSet(viewsets.ModelViewSet):
    """Manage dish categories.

    Only Admin or read-only.
    """
    queryset = DishCategory.objects.all().order_by("id")
    serializer_class = DishCategorySerializer
    lookup_field = 'pk'
    permission_classes = [permissions.IsAdminUser | ReadOnly]


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_summary="Lists all dish labels.",
    operation_description="Returns dish labels."
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_summary="Gets dish label with id={id}.",
    operation_description="Returns dish label."
))
@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_summary="Creates dish label.",
    operation_description="Returns dish label."
))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    operation_summary="Partial updates dish label with id={id}.",
    operation_description="Returns dish label."
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    operation_summary="Updates dish label with id={id}.",
    operation_description="Returns dish label."
))
@method_decorator(name='destroy', decorator=swagger_auto_schema(
    operation_summary="Deletes dish label with id={id}.",
    operation_description="Returns none."
))
class DishLabelViewSet(viewsets.ModelViewSet):
    """Manage dish labels.

    Only Admin or read-only.
    """
    queryset = DishLabel.objects.all().order_by("id")
    serializer_class = DishLabelSerializer
    lookup_field = 'pk'
    permission_classes = [permissions.IsAdminUser | ReadOnly]


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_summary="Lists all dishes.",
    operation_description="Returns dishes."
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_summary="Gets dish with id={id}.",
    operation_description="Returns dish."
))
@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_summary="Creates dish.",
    operation_description="Returns dish."
))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    operation_summary="Partial updates dish with id={id}.",
    operation_description="Returns dish."
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    operation_summary="Updates dish with id={id}.",
    operation_description="Returns dish."
))
@method_decorator(name='destroy', decorator=swagger_auto_schema(
    operation_summary="Deletes dish with id={id}.",
    operation_description="Returns none."
))
class DishViewSet(viewsets.ModelViewSet):
    """Manage dishes.

    Only Admin or read-only.
    """
    queryset = Dish.objects.all().order_by("id")
    serializer_class = DishSerializer
    lookup_field = 'pk'
    permission_classes = [permissions.IsAdminUser | ReadOnly]


# TODO: IngredientViewSet is not needed, because we don't need ingredients/ endpoint... right?
# (Because we could get/modify/create ingredients through the recipes/ endpoint)
@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_summary="Lists all ingredients.",
    operation_description="Returns ingredients."
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_summary="Gets ingredient with id={id}.",
    operation_description="Returns ingredient."
))
@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_summary="Creates ingredient.",
    operation_description="Returns ingredient."
))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    operation_summary="Partial updates ingredient with id={id}.",
    operation_description="Returns ingredient."
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    operation_summary="Updates ingredient with id={id}.",
    operation_description="Returns ingredient."
))
@method_decorator(name='destroy', decorator=swagger_auto_schema(
    operation_summary="Deletes ingredient with id={id}.",
    operation_description="Returns none."
))
class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all().order_by("id")
    serializer_class = IngredientSerializer
    lookup_field = 'pk'


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_summary="Lists all recipes.",
    operation_description="Returns recipes."
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_summary="Gets recipe with id={id}.",
    operation_description="Returns recipe."
))
@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_summary="Creates recipe.",
    operation_description="Returns recipe."
))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    operation_summary="Partial updates recipe with id={id}.",
    operation_description="Returns recipe."
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    operation_summary="Updates recipe with id={id}.",
    operation_description="Returns recipe."
))
@method_decorator(name='destroy', decorator=swagger_auto_schema(
    operation_summary="Deletes recipe with id={id}.",
    operation_description="Returns none."
))
class RecipeViewSet(viewsets.ModelViewSet):
    """Manage recipes.

    Only Admin or read-only.
    """
    queryset = Recipe.objects.all().order_by("id")
    serializer_class = RecipeSerializer
    lookup_field = 'pk'
    parser_class = (FileUploadParser,)
    permission_classes = [permissions.IsAdminUser | ReadOnly]
