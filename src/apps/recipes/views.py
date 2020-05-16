from rest_framework import viewsets
from rest_framework.parsers import FileUploadParser

from apps.recipes.models import Weight, Ingredient, Recipe
from apps.recipes.serializers import WeightSerializer, IngredientSerializer, RecipeSerializer

class WeightViewSet(viewsets.ModelViewSet):
    queryset = Weight.objects.all().order_by("id")
    serializer_class = WeightSerializer
    lookup_field='pk'

class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all().order_by("id")
    serializer_class = IngredientSerializer
    lookup_field='pk'

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by("id")
    serializer_class = RecipeSerializer
    lookup_field='pk'
    parser_class = (FileUploadParser,)
