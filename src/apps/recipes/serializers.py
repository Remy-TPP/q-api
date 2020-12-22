# TODO: test CRUD'ing using serializers
from django.db.models import Q
from rest_framework import serializers
# from rest_framework_recursive.fields import RecursiveField

from apps.recipes.models import DishCategory, DishLabel, Dish, Ingredient, Recipe, Interaction
from apps.products.serializers import AmountSerializer, ProductSerializer, ProductMinimalSerializer


class DishCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = DishCategory
        fields = '__all__'


class DishLabelSerializer(serializers.ModelSerializer):

    class Meta:
        model = DishLabel
        fields = '__all__'


class RecipeMinimalSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ['id', 'title']


class DishSerializer(serializers.ModelSerializer):
    categories = DishCategorySerializer(many=True)
    recipes = RecipeMinimalSerializer(many=True, read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Dish
        exclude = ['labels']

    def get_image(self, obj):
        request = self.context.get("request")
        recipe_with_image = obj.recipes.exclude(
            Q(image__isnull=True) |
            Q(image__exact='')
        ).first()
        return request.build_absolute_uri(recipe_with_image.image.url) if recipe_with_image is not None else None


class IngredientSerializer(AmountSerializer):
    product = ProductSerializer()
    recipe = RecipeMinimalSerializer()
    # substitutions = RecursiveField(allow_null=True, many=True)

    class Meta:
        model = Ingredient
        exclude = ['id']


class RecipeIngredientSerializer(AmountSerializer):
    product = ProductMinimalSerializer()

    class Meta:
        model = Ingredient
        exclude = ['id', 'recipe']


class RecipeSerializer(serializers.ModelSerializer):
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


class InteractionSerializer(serializers.ModelSerializer):
    # TODO: extract min and max as constants
    profile = serializers.StringRelatedField()
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    rating = serializers.DecimalField(max_digits=4, decimal_places=2, min_value=1, max_value=10, required=False)

    class Meta:
        model = Interaction
        exclude = ['id']
        read_only_fields = ['id', 'cooked_at']

    def create(self, validated_data):
        interaction = Interaction.objects.get_or_create(
            profile=validated_data.pop('profile'),
            recipe=validated_data.pop('recipe'),
        )[0]
        try:
            interaction.rating = validated_data.pop('rating')
        except KeyError:
            pass
        interaction.save()
        return interaction
