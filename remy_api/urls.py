from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('api.urls'), name='api'),
    path('api/v1/auth/', include('rest_framework.urls'), name='rest_framework')
]
