from django.urls import include, path
from rest_framework.routers import SimpleRouter

from apps.products.views import UnitViewSet, ProductViewSet


router = SimpleRouter()

router.register(r'units', UnitViewSet)                          # units/            (only admin)
router.register(r'products', ProductViewSet)                    # products/         (only admin)


urlpatterns = [
    path('', include(router.urls)),
]
