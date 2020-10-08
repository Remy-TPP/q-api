from django.urls import include, path
from rest_framework.routers import SimpleRouter

from apps.inventories.views import (PlaceViewSet,
                                    InventoryItemViewSet,
                                    PurchaseDetailView,
                                    PurchaseCreateView,
                                    CartViewSet,
                                    default_place)

router = SimpleRouter()

router.register(r'places', PlaceViewSet, basename='place')                                   # places/
router.register(r'inventoryitems', InventoryItemViewSet, basename='inventoryitems')          # inventoryitems/
router.register(r'cart', CartViewSet, basename='cart')                                       # cart/

urlpatterns = [
    path('', include(router.urls)),
    path('default_place', default_place, name='default-place'),
    path('inventories/purchase/<pk>', PurchaseDetailView.as_view(), name='purchase-detail'),
    path('inventories/generate_qr', PurchaseCreateView.as_view(), name='purchase-create'),
]
