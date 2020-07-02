from django.shortcuts import render
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Remy API",
      default_version='v1',
      description="This is the API of Remy app",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)
