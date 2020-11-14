from rest_framework import serializers

from apps.recommendations.models import Recommendation


class RecommendationSerializer(serializers.ModelSerializer):
    recipe_id = serializers.CharField(source='recipe.id', read_only=True)
    recipe_title = serializers.CharField(source='recipe.title', read_only=True)
    recipe_description = serializers.CharField(source='recipe.description', read_only=True)
    image = serializers.ImageField(source='recipe.image', read_only=True)

    class Meta:
        model = Recommendation
        exclude = ['id', 'profile', 'recipe']
