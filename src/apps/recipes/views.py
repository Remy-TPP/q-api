from rest_framework import viewsets
from rest_framework.parsers import FileUploadParser

from apps.recipes.models import DishCategory, DishLabel, Dish, Ingredient, Recipe
from apps.recipes.serializers import (DishCategorySerializer, DishLabelSerializer, DishSerializer,
                                      IngredientSerializer, RecipeSerializer)


class DishCategoryViewSet(viewsets.ModelViewSet):
    # TODO: document, verify
    queryset = DishCategory.objects.all().order_by("id")
    serializer_class = DishCategorySerializer
    lookup_field = 'pk'


class DishLabelViewSet(viewsets.ModelViewSet):
    # TODO: document, verify
    queryset = DishLabel.objects.all().order_by("id")
    serializer_class = DishLabelSerializer
    lookup_field = 'pk'


class DishViewSet(viewsets.ModelViewSet):
    # TODO: document, verify
    queryset = Dish.objects.all().order_by("id")
    serializer_class = DishSerializer
    lookup_field = 'pk'


# TODO: IngredientViewSet is not needed, because we don't need ingredients/ endpoint... right?
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
