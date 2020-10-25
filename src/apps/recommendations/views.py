from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.recipes.models import Recipe

from apps.recipes.serializers import RecipeSerializer


class RecommendationViewSet(viewsets.GenericViewSet):
    serializer_class = RecipeSerializer

    def get_queryset(self):
        # TODO: filtrar recommendacion por usuario
        # return Recommendation.objects.filter(user=self.request.user)
        return Recipe.objects.all()

    def send_queryset(self, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False)
    def my_recommendations(self, request):
        queryset = self.get_queryset()

        return self.send_queryset(queryset)
