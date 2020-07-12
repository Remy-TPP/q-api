from rest_framework import status, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema

@swagger_auto_schema(
    method='get',
    operation_summary="Get a hello",
    operation_description="Returns hello world."
)
@api_view(['GET', 'POST'])
def hello_world(request):
    if request.method == 'POST':
        return Response({"message": "Got some data!", "data": request.data}, status=status.HTTP_200_OK)
    return Response({"message": "Hello, world!"}, status=status.HTTP_200_OK)
