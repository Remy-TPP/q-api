from django.urls import include, path
from rest_framework.routers import SimpleRouter

from apps.recipes.views import (UnitViewSet,
                                IngredientViewSet,
                                RecipeViewSet,
                                ProductViewSet)

router = SimpleRouter()

router.register(r"units", UnitViewSet)
router.register(r"ingredients", IngredientViewSet)
router.register(r"recipes", RecipeViewSet)
router.register(r"products", ProductViewSet)


urlpatterns = [
    path("", include(router.urls))
]
