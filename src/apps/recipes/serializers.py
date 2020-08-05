# TODO: test CRUD'ing using serializers
from rest_framework import serializers
# from rest_framework_recursive.fields import RecursiveField

from apps.recipes.models import DishCategory, DishLabel, Dish, Ingredient, Recipe
from apps.products.serializers import AmountSerializer, ProductSerializer, ProductMinimalSerializer


class DishCategorySerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = DishCategory
        fields = '__all__'


class DishLabelSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = DishLabel
        fields = '__all__'


class DishSerializer(serializers.HyperlinkedModelSerializer):
    categories = DishCategorySerializer(many=True)
    labels = DishLabelSerializer(many=True)
    recipes = serializers.HyperlinkedRelatedField(view_name='recipe-detail', many=True, read_only=True)

    class Meta:
        model = Dish
        fields = '__all__'


class RecipeMinimalSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Recipe
        fields = ['url', 'title']


class IngredientSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    recipe = RecipeMinimalSerializer()
    amount = AmountSerializer()
    # substitutions = RecursiveField(allow_null=True, many=True)

    class Meta:
        model = Ingredient
        exclude = ['id']

    def create(self, validated_data):
        amount_serializer = self.fields['amount']
        amount = amount_serializer.create(validated_data.pop('amount'))
        validated_data['amount'] = amount

        ingredient = Ingredient.objects.create(**validated_data)
        return ingredient


class RecipeIngredientSerializer(serializers.ModelSerializer):
    product = ProductMinimalSerializer()
    amount = AmountSerializer()

    class Meta:
        model = Ingredient
        exclude = ['id', 'recipe']


class RecipeSerializer(serializers.HyperlinkedModelSerializer):
    image = serializers.ImageField(max_length=None, use_url=False, allow_null=True)
    instructions = serializers.SlugRelatedField(slug_field='steps', read_only=True)
    ingredients = serializers.SerializerMethodField(method_name='get_ingredients')

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_ingredients(self, obj):
        return RecipeIngredientSerializer(
            Ingredient.objects.filter(recipe=obj), many=True, context=self.context
        ).data

    def create(self, validated_data):
        ingredients_serializer = IngredientSerializer(many=True, read_only=True)
        ingredients = ingredients_serializer.create(validated_data.pop('ingredients'))
        recipe = Recipe.objects.create(**validated_data)
        recipe.ingredients.set(ingredients)
        return recipe
