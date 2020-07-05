from django.urls import include, path
from rest_framework.routers import SimpleRouter

from apps.inventories.views import (PlaceViewSet,
                                    InventoryViewSet)

router = SimpleRouter()

router.register(r'places', PlaceViewSet)                             # places/
router.register(r'inventories', InventoryViewSet)                    # inventories/

urlpatterns = [
    path("", include(router.urls)),
]
