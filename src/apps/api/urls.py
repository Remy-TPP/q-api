from django.urls import path, include
from .views import schema_view
from rest_framework.authtoken import views

urlpatterns = [
	path('api-auth/', include('rest_framework.urls')),
    path('token/', views.obtain_auth_token, name='token'),
]


urlpatterns += [
	path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
	path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]


urlpatterns += [
    path('', include('apps.users.urls'), name='users'),
    path('', include('apps.recipes.urls'), name='recipes'),
]