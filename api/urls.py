from django.urls import path, include
from .views import schema_view

urlpatterns = [
	path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
	path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('', include('users.urls'), name='users'),
]
