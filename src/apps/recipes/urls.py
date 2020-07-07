from django.urls import include, path
from rest_framework.routers import SimpleRouter

from apps.recipes.views import (IngredientViewSet,
                                RecipeViewSet)

router = SimpleRouter()

router.register(r"ingredients", IngredientViewSet)              # ingredients/      (not needed)
router.register(r"recipes", RecipeViewSet)                      # recipes/


urlpatterns = [
    path('', include(router.urls)),
]
