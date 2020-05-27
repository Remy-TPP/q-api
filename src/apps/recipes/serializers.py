from rest_framework import serializers

from apps.recipes.models import (Unit,
                                 Amount,
                                 Ingredient,
                                 Recipe,
                                 Product)

class UnitSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Unit
        fields = '__all__'

class AmountSerializer(serializers.ModelSerializer):
    unit = serializers.SlugRelatedField(slug_field='name', queryset=Unit.objects.all())

    class Meta:
        model = Amount
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = '__all__'

class IngredientSerializer(serializers.HyperlinkedModelSerializer):
    amount = AmountSerializer()
    product_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        source='product',
        queryset=Product.objects.all()
    )
    product = serializers.SlugRelatedField(read_only=True, slug_field='name')

    class Meta:
        model = Ingredient
        fields = ('url', 'product', 'amount', 'product_id')

    def create(self, validated_data):
        amount_serializer = self.fields['amount']
        amount = amount_serializer.create(validated_data.pop('amount'))
        validated_data['amount'] = amount
        ingredient = Ingredient.objects.create(**validated_data)
        return ingredient

class RecipeSerializer(serializers.HyperlinkedModelSerializer):
    image = serializers.ImageField(max_length=None, use_url=False, allow_null=True)
    ingredients = IngredientSerializer(many=True)

    def create(self, validated_data):
        ingredients_serializer = self.fields['ingredients']
        ingredients = ingredients_serializer.create(validated_data.pop('ingredients'))
        recipe = Recipe.objects.create(**validated_data)
        recipe.ingredients.set(ingredients)
        return recipe

    class Meta:
        model = Recipe
        fields = '__all__'
