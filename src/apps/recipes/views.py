from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from common.permissions import ReadOnly
from apps.recipes.models import DishCategory, DishLabel, Dish, Recipe
from apps.recipes.serializers import (DishCategorySerializer,
                                      DishLabelSerializer,
                                      DishSerializer,
                                      RecipeSerializer,
                                      InteractionSerializer
                                      )
from apps.recommendations.services import RemyRSService


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_summary="Lists all dish categories.",
    operation_description="Returns dish categories."
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_summary="Gets dish category with id={id}.",
    operation_description="Returns dish category."
))
@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_summary="Creates dish category.",
    operation_description="Returns dish category."
))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    operation_summary="Partial updates dish category with id={id}.",
    operation_description="Returns dish category."
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    operation_summary="Updates dish category with id={id}.",
    operation_description="Returns dish category."
))
@method_decorator(name='destroy', decorator=swagger_auto_schema(
    operation_summary="Deletes dish category with id={id}.",
    operation_description="Returns none."
))
class DishCategoryViewSet(viewsets.ModelViewSet):
    """Manage dish categories.

    Only Admin or read-only.
    """
    queryset = DishCategory.objects.all().order_by("id")
    serializer_class = DishCategorySerializer
    lookup_field = 'pk'
    permission_classes = [permissions.IsAdminUser | ReadOnly]
    search_fields = ['name', 'description']


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_summary="Lists all dish labels.",
    operation_description="Returns dish labels."
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_summary="Gets dish label with id={id}.",
    operation_description="Returns dish label."
))
@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_summary="Creates dish label.",
    operation_description="Returns dish label."
))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    operation_summary="Partial updates dish label with id={id}.",
    operation_description="Returns dish label."
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    operation_summary="Updates dish label with id={id}.",
    operation_description="Returns dish label."
))
@method_decorator(name='destroy', decorator=swagger_auto_schema(
    operation_summary="Deletes dish label with id={id}.",
    operation_description="Returns none."
))
class DishLabelViewSet(viewsets.ModelViewSet):
    """Manage dish labels.

    Only Admin or read-only.
    """
    queryset = DishLabel.objects.all().order_by("id")
    serializer_class = DishLabelSerializer
    lookup_field = 'pk'
    permission_classes = [permissions.IsAdminUser | ReadOnly]
    search_fields = ['name']


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_summary="Lists all dishes.",
    operation_description="Returns dishes."
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_summary="Gets dish with id={id}.",
    operation_description="Returns dish."
))
@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_summary="Creates dish.",
    operation_description="Returns dish."
))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    operation_summary="Partial updates dish with id={id}.",
    operation_description="Returns dish."
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    operation_summary="Updates dish with id={id}.",
    operation_description="Returns dish."
))
@method_decorator(name='destroy', decorator=swagger_auto_schema(
    operation_summary="Deletes dish with id={id}.",
    operation_description="Returns none."
))
class DishViewSet(viewsets.ModelViewSet):
    """Manage dishes.

    Only Admin or read-only.
    """
    queryset = Dish.objects.all().order_by("id")
    serializer_class = DishSerializer
    lookup_field = 'pk'
    permission_classes = [permissions.IsAdminUser | ReadOnly]
    filterset_fields = ['labels', 'categories']
    search_fields = ['name', 'description']


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_summary="Lists all recipes.",
    operation_description="Returns recipes."
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_summary="Gets recipe with id={id}.",
    operation_description="Returns recipe."
))
@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_summary="Creates recipe.",
    operation_description="Returns recipe."
))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    operation_summary="Partial updates recipe with id={id}.",
    operation_description="Returns recipe."
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    operation_summary="Updates recipe with id={id}.",
    operation_description="Returns recipe."
))
@method_decorator(name='destroy', decorator=swagger_auto_schema(
    operation_summary="Deletes recipe with id={id}.",
    operation_description="Returns none."
))
class RecipeViewSet(viewsets.ModelViewSet):
    """Manage recipes.

    Only Admin or read-only.
    """
    queryset = Recipe.objects.all().order_by("id")
    serializer_class = RecipeSerializer
    lookup_field = 'pk'
    parser_class = (FileUploadParser,)
    permission_classes = [permissions.IsAdminUser | ReadOnly]
    filterset_fields = ['dish__labels', 'dish__categories']
    search_fields = ['title', 'description', 'dish__name', 'dish__description']

    def get_serializer(self, *args, **kwargs):
        # we override this method and add ratings in context for serializer
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()

        try:
            ratings_for_user = RemyRSService.get_recommendations_for_user(
                profile_id=self.request.user.profile.id,
                n='all',
            )
            kwargs['context']['ratings'] = {r['recipe_id']: r for r in ratings_for_user}
        except AttributeError:
            # this catches the case that there's no profile (i.e. not logged in)
            pass

        return serializer_class(*args, **kwargs)


@swagger_auto_schema(
    method='put',
    operation_summary='Leave a rating for recipe from current user',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'recipe_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Id of recipe to rate'),
            'rating': openapi.Schema(type=openapi.TYPE_NUMBER, description='Rating given'),
        },
        required=['recipe_id', 'rating'],
    ),
    responses={200: InteractionSerializer()},
)
@api_view(['PUT'])
def rate_recipe(request):
    if not request.data.get('rating'):
        return Response({'message': 'Must provide the recipe and rating'}, status=status.HTTP_400_BAD_REQUEST)

    interaction_serializer = InteractionSerializer(data=request.data)
    interaction_serializer.is_valid(raise_exception=True)
    interaction_serializer.save(profile=request.user.profile)

    return Response(interaction_serializer.data, status=status.HTTP_200_OK)
