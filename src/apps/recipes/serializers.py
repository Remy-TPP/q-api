from rest_framework import serializers
from rest_framework_recursive.fields import RecursiveField

from apps.recipes.models import (Ingredient,
                                 Recipe)
from apps.products.models import Product
from apps.products.serializers import AmountSerializer


class IngredientSerializer(serializers.ModelSerializer):
    amount = AmountSerializer()
    product_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        source='product',
        queryset=Product.objects.all()
    )
    product = serializers.SlugRelatedField(read_only=True, slug_field='name')
    substitutions = RecursiveField(allow_null=True, many=True)

    class Meta:
        model = Ingredient
        fields = ['id', 'amount', 'product', 'product_id', 'substitutions']

    # def get_fields(self):
    #     fields = super(IngredientSerializer, self).get_fields()
    #     fields['substitutions'] = IngredientSerializer(many=True)
    #     return fields

    def create(self, validated_data):
        amount_serializer = self.fields['amount']
        amount = amount_serializer.create(validated_data.pop('amount'))
        validated_data['amount'] = amount

        substitutions_serializer = self.fields['substitutions'].proxied
        substitutions = substitutions_serializer.create(validated_data.pop('substitutions'))

        ingredient = Ingredient.objects.create(**validated_data)
        ingredient.substitutions.set(substitutions)
        return ingredient


class RecipeSerializer(serializers.HyperlinkedModelSerializer):
    image = serializers.ImageField(max_length=None, use_url=False, allow_null=True)
    ingredients = IngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = '__all__'

    def create(self, validated_data):
        ingredients_serializer = self.fields['ingredients']
        ingredients = ingredients_serializer.create(validated_data.pop('ingredients'))
        recipe = Recipe.objects.create(**validated_data)
        recipe.ingredients.set(ingredients)
        return recipe
