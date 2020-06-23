from django.urls import path, include
from django.contrib.auth import views

from apps.api.views import schema_view

urlpatterns = [
    path('api-auth/', include('rest_framework.urls')),
    path('rest-auth/', include('rest_auth.urls')),
    path('rest-auth/registration', include('rest_auth.registration.urls')),
    path('', include('django.contrib.auth.urls'))
]


urlpatterns += [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]


urlpatterns += [
    path('', include('apps.profiles.urls'), name='profiles'),
    path('', include('apps.recipes.urls'), name='recipes'),
]
