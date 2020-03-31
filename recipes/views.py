from rest_framework import generics
from .models import *
from .serializers import *
from django.shortcuts import get_object_or_404
from rest_framework.parsers import FileUploadParser

class Recipes(generics.ListCreateAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    parser_class = (FileUploadParser,)

class Recipe(generics.RetrieveUpdateDestroyAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    lookup_field='pk'
    parser_class = (FileUploadParser,)
