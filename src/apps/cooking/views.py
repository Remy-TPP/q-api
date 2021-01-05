from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from apps.recipes.models import Recipe
from apps.products.models import Amount
from apps.recipes.serializers import InteractionSerializer
from apps.inventories.utils import get_place_or_default


@swagger_auto_schema(
    method='post',
    operation_summary='Cook recipe',
    operation_description='''
        Cook recipe as current user, in place given by ID or in default place.
        Can optionally receive other details for the interaction in the request body, such as rating.
    ''',
    manual_parameters=[
        openapi.Parameter(
            'recipe_id',
            in_=openapi.IN_QUERY,
            description='ID of a recipe',
            type=openapi.TYPE_INTEGER,
            required=True,
        ),
        openapi.Parameter(
            'place_id',
            in_=openapi.IN_QUERY,
            description='ID of a place',
            type=openapi.TYPE_INTEGER,
        ),
    ],
    # TODO: mark as optional
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'rating': openapi.Schema(type=openapi.TYPE_NUMBER, description='Rating given'),
        },
        required=None,
    ),
)
@api_view(['POST'])
def cook_recipe(request):
    recipe_id = request.query_params.get('recipe_id')
    place_id = request.query_params.get('place_id')

    if not recipe_id:
        return Response(
            {'message': 'recipe_id must be provided'},
            status=status.HTTP_400_BAD_REQUEST
        )

    recipe = get_object_or_404(Recipe, id=recipe_id)
    place = get_place_or_default(request.user.profile, place_id)

    if not place:
        return Response(
            {'message': 'Must have at least one item in your inventory'},
            status=status.HTTP_404_NOT_FOUND,
        )

    interaction_serializer = InteractionSerializer(data={**request.data, 'recipe_id': recipe_id})
    interaction_serializer.is_valid(raise_exception=True)

    with transaction.atomic():
        interaction = interaction_serializer.save(profile=request.user.profile)
        interaction.cook()

        for ingredient in recipe.ingredient_set.all():
            # TODO: en la línea de abajo, que pasa si cocina con algo que no tiene?? sustitutos??
            item = place.inventory.filter(product=ingredient.product).first()
            if item:
                item.reduce_amount(Amount(ingredient.quantity, ingredient.unit.id))

    return Response(interaction_serializer.data, status=status.HTTP_200_OK)
