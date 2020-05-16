from django.urls import include, path
from rest_framework.routers import SimpleRouter

from apps.profiles.views import ProfileViewSet, ProfileTypeViewSet, GroupViewSet, UserViewSet

router = SimpleRouter()

router.register(r"profiles", ProfileViewSet)
# router.register(r"users", UserViewSet)
router.register(r"profiletypes", ProfileTypeViewSet)
router.register(r"groups", GroupViewSet)


urlpatterns = [
    path("", include(router.urls))
]