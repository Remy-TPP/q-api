from django.urls import path, include
from django.shortcuts import redirect

from apps.api.views import SchemaView, reset_db


def redirect_to_swagger(request):
    return redirect('/api/v1/swagger')


urlpatterns = [
    path('api-auth/', include('rest_framework.urls')),
    path('rest-auth/', include('rest_auth.urls')),
    path('rest-auth/registration', include('rest_auth.registration.urls')),
    path('reset/', reset_db, name='reset-db'),
    path('', include('django.contrib.auth.urls')),
]


urlpatterns += [
    path('swagger/', SchemaView.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', SchemaView.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]


urlpatterns += [
    path('', include('apps.profiles.urls'), name='profiles'),
    path('', include('apps.products.urls'), name='products'),
    path('', include('apps.recipes.urls'), name='recipes'),
    path('', include('apps.inventories.urls'), name='inventories'),
    path('', include('apps.cooking.urls'), name='cooking'),
    path('', include('apps.recommendations.urls'), name='recommendations'),
    path('', redirect_to_swagger),
]
