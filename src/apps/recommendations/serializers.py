from rest_framework import serializers

from apps.recommendations.models import Recommendation
from apps.recipes.serializers import RecipeSerializer


class RecommendationSerializer(serializers.ModelSerializer):
    recipe = RecipeSerializer()

    class Meta:
        model = Recommendation
        fields = ['recipe']
