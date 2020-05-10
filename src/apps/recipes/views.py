from rest_framework import generics
from django.shortcuts import get_object_or_404
from rest_framework.parsers import FileUploadParser

from apps.recipes.models import *
from apps.recipes.serializers import *

class Weights(generics.ListCreateAPIView):
    queryset = Weight.objects.all()
    serializer_class = WeightSerializer

class Weight(generics.RetrieveUpdateDestroyAPIView):
    queryset = Weight.objects.all()
    serializer_class = WeightSerializer
    lookup_field='pk'

class Ingredients(generics.ListCreateAPIView):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

class Ingredient(generics.RetrieveUpdateDestroyAPIView):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    lookup_field='pk'

class Recipes(generics.ListCreateAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    parser_class = (FileUploadParser,)

class Recipe(generics.RetrieveUpdateDestroyAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    lookup_field='pk'
    parser_class = (FileUploadParser,)
