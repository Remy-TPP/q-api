from django.urls import path, include
from rest_framework.authtoken import views

from .views import schema_view

urlpatterns = [
	path('api-auth/', include('rest_framework.urls')),
    path('token/', views.obtain_auth_token, name='token'),
]


urlpatterns += [
	path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
	path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]


urlpatterns += [
    path('', include('apps.profiles.urls'), name='profiles'),
    path('', include('apps.recipes.urls'), name='recipes'),
]
