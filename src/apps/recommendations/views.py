from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.recommendations.models import Recommendation

from apps.recommendations.serializers import RecommendationSerializer


class RecommendationViewSet(viewsets.GenericViewSet):
    serializer_class = RecommendationSerializer

    def get_queryset(self):
        return Recommendation.objects.filter(profile__user=self.request.user).order_by('-score')

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
