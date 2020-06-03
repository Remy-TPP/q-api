from rest_framework import viewsets, permissions
from rest_framework.parsers import FileUploadParser

from apps.recipes.models import (Unit,
                                 Ingredient,
                                 Recipe,
                                 Product)
from apps.recipes.serializers import (UnitSerializer,
                                      IngredientSerializer,
                                      RecipeSerializer,
                                      ProductSerializer)

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

class IngredientViewSet(viewsets.ModelViewSet):
    """
    Manage ingredients.

    list: Lists all ingredients.

    Returns ingredients.

    retrieve: Gets ingredient with id={id}.

    Returns ingredient.

    create: Creates ingredient.

    Returns ingredient.

    partial_update: Partial updates ingredient with id={id}.

    Returns ingredient.

    update: Updates ingredient with id={id}.

    Returns ingredient.

    delete: Deletes ingredient with id={id}.

    Returns none.
    """
    queryset = Ingredient.objects.all().order_by("id")
    serializer_class = IngredientSerializer
    lookup_field = 'pk'

class RecipeViewSet(viewsets.ModelViewSet):
    """
    Manage recipes.

    list: Lists all recipes.

    Returns recipes.

    retrieve: Gets recipe with id={id}.

    Returns recipe.

    create: Creates recipe.

    Returns recipe.

    partial_update: Partial updates recipe with id={id}.

    Returns recipe.

    update: Updates recipe with id={id}.

    Returns recipe.

    delete: Deletes recipe with id={id}.

    Returns none.
    """
    queryset = Recipe.objects.all().order_by("id")
    serializer_class = RecipeSerializer
    lookup_field = 'pk'
    parser_class = (FileUploadParser,)


