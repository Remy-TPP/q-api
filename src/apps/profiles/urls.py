from django.urls import include, path
from rest_framework.routers import SimpleRouter
from rest_framework_nested import routers

from apps.profiles.views import (ProfileViewSet,
            ProfileTypeViewSet,
            GroupViewSet,
            UserViewSet,
            FriendshipView)

router = SimpleRouter()

router.register(r'profiles', ProfileViewSet)                    # profiles/
router.register(r'profiletypes', ProfileTypeViewSet)            # profilestypes/
router.register(r'groups', GroupViewSet)                        # groups/
router.register(r'friendship', FriendshipView)                  # friendship/

# friendship_router = routers.NestedSimpleRouter(router, r'profiles', lookup='requesting')
# friendship_router.register(r'friendship', FriendshipView)

urlpatterns = [
    path("", include(router.urls)),
    #path("", include(friendship_router.urls))
]