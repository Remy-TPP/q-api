from django.conf import settings
from django.core import management
from django.contrib.admin.views.decorators import staff_member_required
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from drf_yasg.utils import swagger_auto_schema

SchemaView = get_schema_view(
    openapi.Info(
        title="Remy API",
        default_version='v1',
        description="This is the API of Remy app",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


@swagger_auto_schema(
    method='post',
    operation_summary='Reset the database',
    operation_description=(
        '(Re)populates database with test data, including Units, Recipes & Dishes, DishLabels.\n\n'
        'Warning: this overwrites all db objects with the PK specified by the fixtures, '
        'so any modifications to those will be lost.'
    ),
    manual_parameters=[
        openapi.Parameter(
            'dishes_fixture',
            in_=openapi.IN_QUERY,
            description='Name of fixture to load for recipes and such.',
            type=openapi.TYPE_STRING,
            required=False
        ),
    ],
    security=None,
)
@api_view(['POST'])
@staff_member_required
def reset_db(request):
    dishes_fixture_name = request.query_params.get('dishes_fixture', 'dishes_dataset')
    # TODO: log? "Loading fixtures unit and {dishes_fixture_name}"
    management.call_command('loaddata', 'unit')
    try:
        management.call_command('loaddata', dishes_fixture_name)
    except management.CommandError as err:
        return Response({'error': 'Fixture not found', 'errorMessage': str(err)}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'message': 'Fixtures loaded successfully'}, status=status.HTTP_201_CREATED)
