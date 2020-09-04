from django.core import management
from django.contrib.admin.views.decorators import staff_member_required
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

SchemaView = get_schema_view(
    openapi.Info(
        title="Remy API",
        default_version='v1',
        description="This is the API of Remy app",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


# @method_decorator(name='create', decorator=swagger_auto_schema(
#     operation_summary="Creates a purchase with the given items.",
#     operation_description="Returns image (content_type 'image/jpeg') of QR code with purchase URL embedded.",
#     responses={status.HTTP_201_CREATED: Image},
# ))
# TODO: comment
@api_view(['POST'])
@staff_member_required
def reset_db(request):
    """Populates database with certain test data, including Units, Recipes & Dishes, DishLabels."""
    management.call_command('loaddata', 'unit')
    # TODO: request.query_params.get('dishes_fixture')
    management.call_command('loaddata', 'dishes_dataset_02')
    return Response({'message': 'Fixtures loaded successfully'}, status=status.HTTP_201_CREATED)
