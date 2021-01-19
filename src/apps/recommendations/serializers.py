from rest_framework import serializers

from apps.recipes.models import Recipe
from apps.recipes.serializers import RecommendedRecipeSerializer
from apps.recommendations.models import RecipeRecommendation


class RecipeRecommendationSerializer(serializers.ModelSerializer):
    recipe_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Recipe.objects.all())
    recipe = RecommendedRecipeSerializer(read_only=True)
    rating = serializers.DecimalField(max_digits=4, decimal_places=2, min_value=1, max_value=10)

    class Meta:
        model = RecipeRecommendation
        exclude = ['id']
