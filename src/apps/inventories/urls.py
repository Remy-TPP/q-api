from django.urls import include, path
from rest_framework.routers import SimpleRouter

from apps.inventories.views import (PlaceViewSet,
                                    InventoryViewSet,
                                    InventoryItemViewSet)

router = SimpleRouter()

router.register(r'places', PlaceViewSet)                             # places/
router.register(r'inventories', InventoryViewSet)                    # inventories/
router.register(r'places', InventoryItemViewSet)                    # items/

urlpatterns = [
    path("", include(router.urls)),
]
