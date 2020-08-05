from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from apps.recipes.models import Recipe

from apps.inventories.utils import get_place_or_default


@swagger_auto_schema(
    method='post',
    operation_summary='Cook a recipe',
    operation_description='Cook a recipe in a given or default place',
    manual_parameters=[
        openapi.Parameter(
            'recipe_id',
            in_=openapi.IN_QUERY,
            description='ID of a recipe',
            type=openapi.TYPE_INTEGER,
            required=True
        ),
        openapi.Parameter(
            'place_id',
            in_=openapi.IN_QUERY,
            description='ID of a place',
            type=openapi.TYPE_INTEGER
        ),
    ]
)
@api_view(['POST'])
def cook_recipe(request):
    recipe_id = request.query_params.get('recipe_id')
    place_id = request.query_params.get('place_id')

    if recipe_id:
        recipe = get_object_or_404(Recipe, id=recipe_id)
        place = get_place_or_default(request.user.profile, place_id)

        for ingredient in recipe.ingredients.all():
            # TODO: en la linea de abajo, que pasa si cocina con algo que no tiene?? sustitutos??
            item = place.inventory.items.filter(product=ingredient.product).first()
            if item:
                item.reduce_amount(ingredient.amount)
        return Response({'message': 'Happy cook!'}, status=status.HTTP_200_OK)
    return Response({'message': 'recipe_id must be provided!'}, status=status.HTTP_400_BAD_REQUEST)
