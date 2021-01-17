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


# TODO: to make strictly read-only, can use BaseSerializer and implement to_representation
class RecipeRecommendationSerializer(serializers.ModelSerializer):
    recipe_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Recipe.objects.all())
    recipe = RecommendedRecipeSerializer(read_only=True)
    rating = serializers.DecimalField(max_digits=4, decimal_places=2, min_value=1, max_value=10)
    # rating_is_real = serializers.BooleanField(source='real')

    class Meta:
        model = RecipeRecommendation
        # exclude = ['id', 'recipe']
        exclude = ['id']

    # def to_representation(self, instance):
    #     response = super().to_representation(instance)
    #     print(instance)
    #     # response['recipe'] = RecommendedRecipeSerializer(
    #     #     Recipe.objects.get(pk=instance['recipe_id'])
    #     # ).data
    #     # response['recipe'] = RecommendedRecipeSerializer(instance['recipe_id']).data
    #     print('---')
    #     print(response)
    #     return response
