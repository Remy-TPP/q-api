from django.urls import include, path
from rest_framework_nested import routers
from rest_framework.routers import SimpleRouter

from apps.inventories.views import (PlaceViewSet,
                                    InventoryViewSet,
                                    InventoryItemViewSet)

router = routers.SimpleRouter()

router.register(r'places', PlaceViewSet)                             # places/
router.register(r'inventories', InventoryViewSet)                    # inventories/

places_router = routers.NestedSimpleRouter(router, r'places', lookup='place')
places_router.register(r'items', InventoryItemViewSet)
# router.register(r'places', InventoryItemViewSet)                    # places/{id}/add_item
# router.register(r'items', InventoryItemViewSet)                    # items/

urlpatterns = [
    path("", include(router.urls)),
    path("", include(places_router.urls)),
]
