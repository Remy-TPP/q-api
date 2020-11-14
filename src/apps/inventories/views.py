from PIL import Image
from rest_framework import viewsets, status, generics, mixins
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.http import HttpResponse
from django.db.models import Q
from django.db.transaction import atomic, savepoint, savepoint_commit, savepoint_rollback
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from apps.inventories.utils import get_place_or_default
from apps.inventories.models import (Place,
                                     InventoryItem,
                                     PlaceMember,
                                     Purchase,
                                     Cart,
                                     )
from apps.inventories.serializers import (PlaceSerializer,
                                          InventoryItemSerializer,
                                          PurchaseSerializer,
                                          CartSerializer
                                          )
from apps.recipes.models import (Recipe, Ingredient)
from common.utils import qr_image_from_string


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_summary="Lists all the places the user has.",
    operation_description="Returns places."
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_summary="Gets the place with id={id}..",
    operation_description="Returns place."
))
@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_summary="Creates a place for that user.",
    operation_description="Returns place."
))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    operation_summary="Partial updates place with id={id}.",
    operation_description="Returns place."
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    operation_summary="Updates place with id={id}.",
    operation_description="Returns place."
))
class PlaceViewSet(viewsets.GenericViewSet,
                   mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.ListModelMixin,
                   mixins.RetrieveModelMixin):
    serializer_class = PlaceSerializer
    lookup_field = 'pk'
    search_fields = ['name']

    def get_queryset(self):
        user = self.request.user
        return self.filter_queryset(Place.objects.filter(members=user.profile).order_by("id"))


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_summary="Lists all items that place has.",
    operation_description="Returns items.",
    manual_parameters=[
        openapi.Parameter(
            'place',
            in_=openapi.IN_QUERY,
            description='Place. If wrong or null, default one is going to be used.',
            type=openapi.TYPE_STRING,
            required=False
        ),
    ]
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_summary="Gets the item with id={id}.",
    operation_description="Returns item.",
    manual_parameters=[
        openapi.Parameter(
            'place',
            in_=openapi.IN_QUERY,
            description='Place. If wrong or null, default one is going to be used.',
            type=openapi.TYPE_STRING,
            required=False
        ),
    ]
))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    operation_summary="Partial updates item with id={id}.",
    operation_description="Returns item."
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    operation_summary="Updates item with id={id}.",
    operation_description="Returns item."
))
@method_decorator(name='destroy', decorator=swagger_auto_schema(
    operation_summary="Deletes item with id={id}.",
    operation_description="Returns none."
))
class InventoryItemViewSet(viewsets.GenericViewSet,
                           mixins.CreateModelMixin,
                           mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin):
    serializer_class = InventoryItemSerializer
    lookup_field = 'pk'
    search_fields = ['product__name']

    def get_queryset(self):
        place = get_place_or_default(self.request.user.profile, self.request.query_params.get('place'))
        return self.filter_queryset(InventoryItem.objects.filter(place=place).order_by('id'))

    @swagger_auto_schema(
        operation_summary="Create an item for that place.",
        operation_description="Returns the item.",
        manual_parameters=[
            openapi.Parameter(
                'place',
                in_=openapi.IN_QUERY,
                description='Place. If wrong or null, default one is going to be used.',
                type=openapi.TYPE_STRING,
                required=False
            ),
        ]
    )
    def create(self, request, *args, **kwargs):
        place = get_place_or_default(request.user.profile, request.query_params.get('place'))

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            if place:
                # place_id is correct for this user or has default one
                serializer.save(place=place)
            else:
                # user does not have a place yet
                serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            {
                'msg': "Cannot add Item!",
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    @swagger_auto_schema(
        method='post',
        operation_summary='Create a list of items for that place.',
        operation_description='Choose a place you are member as a default place',
        manual_parameters=[
            openapi.Parameter(
                'place',
                in_=openapi.IN_QUERY,
                description='Place. If wrong or null, default one is going to be used.',
                type=openapi.TYPE_STRING,
                required=False
            ),
        ]
    )
    @action(detail=False, methods=['POST'])
    @atomic
    def add_items(self, request):
        sid = savepoint()
        if 'items' not in request.data:
            return Response({'message': 'Should provide items key!'}, status=status.HTTP_400_BAD_REQUEST)

        for item in request.data.get('items'):
            # TODO: mejorar para que no tenga que pedir el place siempre
            place = get_place_or_default(request.user.profile, request.query_params.get('place'))

            serializer = self.get_serializer(data=item)
            if serializer.is_valid():
                if place:
                    # place_id is correct for this user or has default one
                    serializer.save(place=place)
                else:
                    # user does not have a place yet
                    serializer.save()
            else:
                savepoint_rollback(sid)
                return Response(
                    {
                        'msg': "Cannot add Item!",
                        'errors': serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        savepoint_commit(sid)
        return Response({'message': 'All the items were created!'}, status=status.HTTP_201_CREATED)


@swagger_auto_schema(
    method='post',
    operation_summary='Default place',
    operation_description='Choose a place you are member as a default place',
    manual_parameters=[
        openapi.Parameter(
            'place_id',
            in_=openapi.IN_QUERY,
            description='ID of a place',
            type=openapi.TYPE_INTEGER,
            required=True
        ),
    ]
)
@api_view(['POST'])
def default_place(request):
    place_id = request.query_params.get('place_id')

    if place_id:
        PlaceMember.objects.filter(
            Q(member_id=request.user.profile) &
            Q(is_the_default_one=True)
        ).update(is_the_default_one=False)

        PlaceMember.objects.filter(
            Q(member_id=request.user.profile) &
            Q(place_id=place_id)
        ).update(is_the_default_one=True)
        return Response({'message': 'Your place has changed!'}, status=status.HTTP_200_OK)
    return Response({'message': 'place_id must be provided!'}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_summary="Gets the purchase with uuid={id}.",
    operation_description="Returns purchase.",
))
class PurchaseDetailView(generics.RetrieveAPIView):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    lookup_field = 'pk'
    permission_classes = []


# TODO: not working
@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_summary="Creates a purchase with the given items.",
    operation_description="Returns image (content_type 'image/jpeg') of QR code with purchase URL embedded.",
    responses={status.HTTP_201_CREATED: Image},
))
class PurchaseCreateView(generics.CreateAPIView):
    serializer_class = PurchaseSerializer
    lookup_field = 'pk'
    # TODO: Limit creation of purchases to users? Maybe a certain role? This functionality is intended for sellers
    permission_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        try:
            qr_img = qr_image_from_string(serializer.data['url'])
        except KeyError:
            # TODO: error catch is too specific? lack of message too vague?
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        image_response = HttpResponse(status=status.HTTP_201_CREATED, content_type="image/jpeg")
        qr_img.save(image_response, "JPEG")
        return image_response


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_summary="Lists all items that cart has.",
    operation_description="Returns items.",
    manual_parameters=[
        openapi.Parameter(
            'place',
            in_=openapi.IN_QUERY,
            description='Place. If wrong or null, default one is going to be used.',
            type=openapi.TYPE_STRING,
            required=False
        ),
    ]
))
@method_decorator(name='destroy', decorator=swagger_auto_schema(
    operation_summary="Deletes item with id={id}.",
    operation_description="Returns none."
))
class CartViewSet(viewsets.GenericViewSet,
                  mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.DestroyModelMixin):
    serializer_class = CartSerializer
    lookup_field = 'pk'
    search_fields = ['product__name', 'place__name']

    def get_queryset(self):
        place = get_place_or_default(self.request.user.profile, self.request.query_params.get('place'))
        return self.filter_queryset(Cart.objects.filter(place=place).order_by('product__name'))

    @swagger_auto_schema(
        operation_summary="Create an item for the cart in that place.",
        operation_description="Returns the item.",
        manual_parameters=[
            openapi.Parameter(
                'place',
                in_=openapi.IN_QUERY,
                description='Place. If wrong or null, default one is going to be used.',
                type=openapi.TYPE_STRING,
                required=False
            ),
        ]
    )
    def create(self, request, *args, **kwargs):
        place = get_place_or_default(request.user.profile, request.query_params.get('place'))

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            if place:
                # place_id is correct for this user or has default one
                serializer.save(place=place)
            else:
                # user does not have a place yet
                serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            {
                'msg': "Cannot add item to cart!",
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    @swagger_auto_schema(
        method='post',
        operation_summary='Create a list of items for the cart in that place.',
        manual_parameters=[
            openapi.Parameter(
                'place',
                in_=openapi.IN_QUERY,
                description='Place. If wrong or null, default one is going to be used.',
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'recipe',
                in_=openapi.IN_QUERY,
                description='Recipe.',
                type=openapi.TYPE_STRING,
                required=True
            ),
        ]
    )
    @action(detail=False, methods=['POST'])
    @atomic
    def add_recipe(self, request):
        sid = savepoint()
        recipe_id = request.query_params.get('recipe')
        if not recipe_id:
            return Response({'message': 'Must provide the recipe!'}, status=status.HTTP_400_BAD_REQUEST)

        recipe = get_object_or_404(Recipe.objects.all(), id=recipe_id)
        ingredients = Ingredient.objects.filter(recipe=recipe)
        place = get_place_or_default(self.request.user.profile, self.request.query_params.get('place'))

        for ingredient in ingredients:
            # TODO: mejorar para que no tenga que pedir el place siempre
            place = get_place_or_default(request.user.profile, request.query_params.get('place'))

            serializer = self.get_serializer(data={
                'quantity': ingredient.quantity,
                'unit': ingredient.unit,
                'product': ingredient.product
            })
            if serializer.is_valid():
                if place:
                    # place_id is correct for this user or has default one
                    serializer.save(place=place)
                else:
                    # user does not have a place yet
                    serializer.save()
            else:
                savepoint_rollback(sid)
                return Response(
                    {
                        'msg': "Cannot add item to cart!",
                        'errors': serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        savepoint_commit(sid)
        return Response({'message': 'All the items were created!'}, status=status.HTTP_201_CREATED)
