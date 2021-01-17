from distutils.util import strtobool

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.db.models import Q, prefetch_related_objects
from requests.exceptions import RequestException

from apps.inventories.utils import get_place_or_default
from apps.recipes.models import Recipe
from apps.recommendations.models import Recommendation, RecipeRecommendation
from apps.recommendations.serializers import RecommendationSerializer, RecipeRecommendationSerializer
from apps.recommendations.services import RemyRSService


class Recommendation2ViewSet(viewsets.GenericViewSet):
    serializer_class = RecipeRecommendationSerializer
    search_fields = ['recipe__title', 'recipe__description']

    def get_queryset(self):
        try:
            recommendations = RemyRSService.get_recommendations_for_user(
                # TODO: temp value for tests
                profile_id=2,
                # profile_id=self.request.user.profile_id,
                n='all',
            )
        except (RequestException, RemyRSService.RecSysException):
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # # TODO: TEMPORARY PATCH before fixing irid vs rrid in remy-rs
        # for i, r in enumerate(recommendations):
        #     r['recipe_id'] += 276
        #     r['rating_is_real'] = r['real']
        #     recommendations[i] = r
        # # END of temp patch

        all_recipes = Recipe.objects.all()  # TODO: prefetch?

        # TODO: TEMPORARY PATCH before fixing irid vs rrid in remy-rs: `+276`
        recommendations = [
            RecipeRecommendation(recipe=all_recipes.get(pk=r['recipe_id']+276), rating=r['rating'], rating_is_real=r['real'])
            for r in recommendations
        ]
        recommendations.sort(key=lambda r: -r.rating)
        # recommendations = RecipeRecommendationSerializer(data=recommendations, many=True)
        # print(recommendations.is_valid(raise_exception=True))

        return recommendations

    def postprocess_recommendations(self, recommendations, place, needs_all_ingredients=False):
        if not needs_all_ingredients:
            return recommendations

        prefetch_related_objects(recommendations, 'recipe__ingredient_set__product', 'recipe__ingredient_set__unit')

        # grab user's inventory
        user_inventory = place.inventory.all()
        filtered_recs = []

        for recommendation in recommendations:
            # make a copy of the inventory
            aux_inventory = list(user_inventory)
            prefetch_related_objects(user_inventory, 'product', 'unit')

            # substract each recipe ingredient from inventory until something's missing
            for ingredient in recommendation.recipe.ingredient_set.all():
                if not ingredient.quantity:
                    # ignore non-quantified ingredients (TODO: maybe should check that it exists in inventory?)
                    continue
                try:
                    # look for ingredient in inventory
                    inventory_item = next(
                        (ii for ii in aux_inventory if (ii.product_id == ingredient.product_id and ii.quantity > 0))
                    )
                except StopIteration:
                    # missing ingredient, won't recommend this recipe
                    break
                # substract amount from inventory and check whether there's enough
                if (inventory_item - ingredient) and (inventory_item.quantity < 0):
                    # # TODO: temp just for test; see if insufficient ingr was changed in original inventory
                    # print('insufficient:', inventory_item)
                    # print('in orig inv:', user_inventory.filter(product_id=inventory_item.product_id))
                    # missing something, won't recommend this recipe
                    break
            else:
                # because nothing was missing, recommend recipe
                filtered_recs.append(recommendation)
                # TODO: break if enough recommendations? or delete this?
                if len(filtered_recs) >= 10:
                    break

            # # ...
            # # TODO: any simpler way of doing this?
            # # TODO: should these be products?
            # recipe_ingredients = recomm.recipe.ingredients.distinct('id').values_list('id', flat=True)
            # recipe_products_present_in_inventory = user_inventory_items.filter(
            #     Q(product_id__in=recipe_ingredients)
            # ).distinct('product_id').values_list('product_id', flat=True)

            # if recipe_products_present_in_inventory.count() < recipe_ingredients.count():
            #     # TODO: will probably fail for lack of id
            #     recommendations = recommendations.exclude(id=recomm.id)

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
        needs_all_ingredients = strtobool(self.request.query_params.get('needs_all_ingredients', 'false'))
        # TODO: remove temp
        # place = get_place_or_default(self.request.user.profile, self.request.query_params.get('place_id'))
        from apps.profiles.models import Profile
        place = get_place_or_default(Profile.objects.get(user_id=3), self.request.query_params.get('place_id'))

        if needs_all_ingredients and not place:
            return Response({"error": "You don't have a place"}, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.get_queryset()
        queryset = self.postprocess_recommendations(queryset, place, needs_all_ingredients)
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
