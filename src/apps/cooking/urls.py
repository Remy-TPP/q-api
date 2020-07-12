from django.urls import include, path
from rest_framework.routers import SimpleRouter

from apps.cooking.views import hello_world


urlpatterns = [
    path("hello", hello_world),
]
