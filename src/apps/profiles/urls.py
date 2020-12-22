from django.urls import include, path
from rest_framework.routers import SimpleRouter

from apps.profiles.views import (ProfileViewSet,
                                 ProfileTypeViewSet,
                                 EventViewSet,
                                 FriendshipRequestViewSet,
                                 FriendshipStatusViewSet,
                                 )

router = SimpleRouter()

router.register(r'profiles', ProfileViewSet)                    # profiles/
router.register(r'profiletypes', ProfileTypeViewSet)            # profilestypes/       (only admin)
router.register(r'events', EventViewSet)                        # events/
router.register(r'friendship', FriendshipRequestViewSet)        # friendship/
router.register(r'friendshipstatus', FriendshipStatusViewSet)   # friendshipstatus/    (only admin)


urlpatterns = [
    path("", include(router.urls)),
    # path("", include(friendship_router.urls)),
]
