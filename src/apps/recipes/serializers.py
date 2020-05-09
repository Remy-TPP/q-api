from rest_framework import serializers

from .models import *

class WeightSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Weight
        fields = '__all__'

class AmountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Amount
        fields = '__all__'

class IngredientSerializer(serializers.HyperlinkedModelSerializer):
    amount = AmountSerializer()
    class Meta:
        model = Ingredient
        fields = '__all__'

    def create(self, validated_data):
        amount = Amount.objects.create(**validated_data.pop('amount'))
        validated_data['amount'] = amount
        ingredient = Ingredient.objects.create(**validated_data)
        return ingredient

class RecipeSerializer(serializers.HyperlinkedModelSerializer):
    image = serializers.ImageField(max_length=None, use_url=False)

    class Meta:
        model = Recipe
        fields = '__all__'
