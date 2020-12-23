from distutils.util import strtobool

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.db.models import Q
from requests.exceptions import RequestException

from apps.inventories.utils import get_place_or_default
from apps.recommendations.models import Recommendation
from apps.recommendations.serializers import RecommendationSerializer, RecipeRecommendationSerializer
from apps.recommendations.services import RemyRSService


class Recommendation2ViewSet(viewsets.GenericViewSet):
    serializer_class = RecipeRecommendationSerializer
    search_fields = ['recipe__title', 'recipe__description']

    def get_queryset(self):
        place = get_place_or_default(self.request.user.profile, self.request.query_params.get('place_id'))
        needs_all_ingredients = self.request.query_params.get('needs_all_ingredients')

        try:
            recommendations = RemyRSService.get_recommendations_for_user(
                profile_id=self.request.user.profile.pk,
                n=100
            )
        except (RequestException, RemyRSService.RecommenderSystemException):
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        user_inventory_items = place.inventory.all()

        if needs_all_ingredients and strtobool(needs_all_ingredients):
            for rec in recommendations:
                # TODO: any simpler way of doing this?
                # TODO: should these be products?
                recipe_ingredients = rec.recipe.ingredients.distinct('id').values_list('id', flat=True)
                recipe_products_present_in_inventory = user_inventory_items.filter(
                    Q(product_id__in=recipe_ingredients)
                ).distinct('product_id').values_list('product_id', flat=True)

                if recipe_products_present_in_inventory.count() < recipe_ingredients.count():
                    # TODO: will probably fail for lack of id
                    recommendations = recommendations.exclude(id=rec.id)

        # TODO: remove
        # for rec in recommendations:
        #     print(rec)

        return recommendations

    def _send_queryset(self, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        method='get',
        operation_summary='Get recommended recipes for current user',
        manual_parameters=[
            openapi.Parameter(
                'place_id',
                in_=openapi.IN_QUERY,
                description='Place. If wrong or null, default is used.',
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
            openapi.Parameter(
                'needs_all_ingredients',
                in_=openapi.IN_QUERY,
                description="Whether place must have all of a recipe's ingredients for the recipe to be recommended.",
                type=openapi.TYPE_BOOLEAN,
                required=False,
            ),
        ],
    )
    @action(detail=False)
    def recommend_me(self, request):
        queryset = self.get_queryset()
        return self._send_queryset(queryset)


# TODO: old one, delete view, model, serializer
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

        if all_ingredients and strtobool(all_ingredients):
            for rec in recommendations:
                ingredients_products = rec.recipe.ingredients.distinct('id').values_list('id', flat=True)

                inventory_products = inventory_items.filter(
                    Q(product_id__in=ingredients_products)
                ).distinct('product_id').values_list('product_id', flat=True)
                if inventory_products.count() < ingredients_products.count():
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
                description='Place. If wrong or null, default is used.',
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
