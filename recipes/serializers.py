from .models import *
from rest_framework import serializers

class RecipeSerializer(serializers.HyperlinkedModelSerializer):
    image = serializers.ImageField(max_length=None, use_url=False)

    class Meta:
        model = Recipe
        fields = '__all__'
