from rest_framework import serializers

from apps.recipes.models import Recipe
from apps.recipes.serializers import RecommendedRecipeSerializer
from apps.recommendations.models import Recommendation, RecipeRecommendation


# TODO: remove
class RecommendationSerializer(serializers.ModelSerializer):
    recipe_id = serializers.CharField(source='recipe.id', read_only=True)
    recipe_title = serializers.CharField(source='recipe.title', read_only=True)
    recipe_description = serializers.CharField(source='recipe.description', read_only=True)
    image = serializers.ImageField(source='recipe.image', read_only=True)

    class Meta:
        model = Recommendation
        exclude = ['id', 'profile', 'recipe']


class RecipeRecommendationSerializer(serializers.ModelSerializer):
    recipe_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Recipe.objects.all())
    recipe = RecommendedRecipeSerializer(read_only=True)
    rating = serializers.DecimalField(max_digits=4, decimal_places=2, min_value=1, max_value=10)

    class Meta:
        model = RecipeRecommendation
        exclude = ['id']
