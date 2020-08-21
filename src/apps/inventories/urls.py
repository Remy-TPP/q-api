from django.urls import include, path
from rest_framework.routers import SimpleRouter

from apps.inventories.views import (PlaceViewSet,
                                    InventoryItemViewSet,
                                    PurchaseCreateView,
                                    default_place)

router = SimpleRouter()

router.register(r'places', PlaceViewSet, basename='place')                                   # places/
router.register(r'inventoryitems', InventoryItemViewSet, basename='inventoryitems')          # inventoryitems/

urlpatterns = [
    path('', include(router.urls)),
    path('default_place', default_place, name='default-place'),
    path('inventories/generate_qr', PurchaseCreateView.as_view()),
]
