from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.db.models import Q
from apps.inventories.utils import get_place_or_default

from apps.recommendations.models import Recommendation
from apps.recommendations.serializers import RecommendationSerializer


class RecommendationViewSet(viewsets.GenericViewSet):
    serializer_class = RecommendationSerializer
    search_fields = ['recipe__title', 'recipe__description']

    def get_queryset(self):
        place = get_place_or_default(self.request.user.profile, self.request.query_params.get('place'))
        all_ingredients = self.request.query_params.get('all_ingredients')

        inventory_items = place.inventory.all()
        recommendations = self.filter_queryset(
            Recommendation.objects.filter(
                Q(profile__user=self.request.user.id)
            ).order_by('-score')
        )

        if bool(all_ingredients) is True:
            for rec in recommendations:
                item = inventory_items.filter(
                    Q(product__in=rec.recipe.ingredients.values_list('id', flat=True))
                )
                if item.count() != rec.recipe.ingredients.count():
                    recommendations = recommendations.exclude(id=rec.id)

        return recommendations

    def send_queryset(self, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        method='get',
        operation_summary='Get my recommendations.',
        manual_parameters=[
            openapi.Parameter(
                'place',
                in_=openapi.IN_QUERY,
                description='Place. If wrong or null, default one is going to be used.',
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'all_ingredients',
                in_=openapi.IN_QUERY,
                description='Boolean to define if I need to have all ingredients. Default: false.',
                type=openapi.TYPE_BOOLEAN,
                required=False
            ),
        ]
    )
    @action(detail=False)
    def my_recommendations(self, request):
        queryset = self.get_queryset()
        return self.send_queryset(queryset)
