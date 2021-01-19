from copy import deepcopy
from distutils.util import strtobool

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.db.models import prefetch_related_objects
from requests.exceptions import RequestException

from apps.inventories.utils import get_place_or_default
from apps.recipes.models import Recipe
from apps.recommendations.models import RecipeRecommendation
from apps.recommendations.serializers import RecipeRecommendationSerializer
from apps.recommendations.services import RemyRSService


class RecommendationViewSet(viewsets.GenericViewSet):
    serializer_class = RecipeRecommendationSerializer
    search_fields = ['recipe__title', 'recipe__description']

    def get_queryset(self):
        # TODO: actually returns a list, fix wording?
        recommendations = RemyRSService.get_recommendations_for_user(
            # TODO: temp value for tests
            # profile_id=2,
            profile_id=self.request.user.profile.id,
            n='all',
        )

        all_recipes = Recipe.objects.all()  # TODO: prefetch?

        recommendations = [
            # TODO: remove TEMPORARY PATCH after fixing irid vs rrid in remy-rs: `+276`
            RecipeRecommendation(recipe=all_recipes.get(pk=r['recipe_id']+276),
                                 rating=r['rating'], rating_is_real=r['real'])
            for r in recommendations
        ]
        recommendations.sort(key=lambda r: -r.rating)

        return recommendations

    def postprocess_recommendations(self, recommendations, place, need_all_ingredients=False):
        if not need_all_ingredients:
            return recommendations

        prefetch_related_objects(recommendations, 'recipe__ingredient_set__product', 'recipe__ingredient_set__unit')

        # get and prefetch user's inventory
        user_inventory = place.inventory.all().prefetch_related('product', 'unit')
        list_inventory = list(user_inventory)
        prefetch_related_objects(list_inventory, 'product', 'unit')

        filtered_recs = []
        for recommendation in recommendations:
            # make a copy of the inventory to play with
            aux_inventory = deepcopy(list_inventory)

            # substract each recipe ingredient from inventory to find if something's missing
            for ingredient in recommendation.recipe.ingredient_set.all():
                if not ingredient.quantity:
                    # ignore non-quantified ingredients (TODO: maybe should check that it exists in inventory?)
                    continue
                try:
                    # look for ingredient in inventory
                    inventory_item = next(
                        (ii for ii in aux_inventory
                         if (ii.product_id == ingredient.product_id and ii.quantity > 0))
                    )
                except StopIteration:
                    # missing ingredient, won't recommend this recipe
                    break
                # substract amount from inventory and check whether there's enough
                if (inventory_item - ingredient) and (inventory_item.quantity < 0):
                    # missing something, won't recommend this recipe
                    break
            else:
                # because nothing was missing, recommend recipe
                filtered_recs.append(recommendation)
                # TODO: break if enough recommendations? or delete this?
                if len(filtered_recs) >= 10:
                    break

        return filtered_recs


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
                'need_all_ingredients',
                in_=openapi.IN_QUERY,
                description="Whether place must have all of a recipe's ingredients for the recipe to be recommended.",
                type=openapi.TYPE_BOOLEAN,
                required=False,
            ),
        ],
    )
    @action(detail=False, methods=['GET'], url_path='recommend_me', url_name='recommend-me')
    def recommend_me(self, request):
        need_all_ingredients = strtobool(self.request.query_params.get('need_all_ingredients', 'false'))
        # TODO: remove temp
        # from apps.profiles.models import Profile
        # place = get_place_or_default(Profile.objects.get(user_id=3), self.request.query_params.get('place_id'))
        place = get_place_or_default(self.request.user.profile, self.request.query_params.get('place_id'))

        if need_all_ingredients and not place:
            return Response({"error": "You don't have a place"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            queryset = self.get_queryset()
        except (RequestException, RemyRSService.RecSysException) as rs_error:
            return Response({"error": repr(rs_error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        queryset = self.postprocess_recommendations(queryset, place, need_all_ingredients)
        return self._send_queryset(queryset)
