from django.urls import include, path
from rest_framework_nested import routers

from apps.inventories.views import (PlaceViewSet,
                                    InventoryViewSet,
                                    InventoryItemViewSet,
                                    default_place)

router = routers.SimpleRouter()

router.register(r'places', PlaceViewSet)                             # places/
router.register(r'inventories', InventoryViewSet)                    # inventories/

places_router = routers.NestedSimpleRouter(router, r'places', lookup='place')
places_router.register(r'items', InventoryItemViewSet, basename='items')

urlpatterns = [
    path("", include(router.urls)),
    path("", include(places_router.urls)),
    path('default_place', default_place, name='default-place'),
]
