from django.urls import include, path
from rest_framework.routers import SimpleRouter

from apps.recipes.views import (UnitViewSet,
                                IngredientViewSet,
                                RecipeViewSet,
                                ProductViewSet)

router = SimpleRouter()

router.register(r"units", UnitViewSet)                          # units/            (only admin)
router.register(r"ingredients", IngredientViewSet)              # ingredients/      (not needed)
router.register(r"recipes", RecipeViewSet)                      # recipes/
router.register(r"products", ProductViewSet)                    # products/         (only admin)


urlpatterns = [
    path('', include(router.urls)),
]
