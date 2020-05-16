from django.urls import include, path
from rest_framework.routers import SimpleRouter

from apps.recipes.views import WeightViewSet, IngredientViewSet, RecipeViewSet

router = SimpleRouter()

router.register(r"weights", WeightViewSet)
router.register(r"ingredients", IngredientViewSet)
router.register(r"recipes", RecipeViewSet)


urlpatterns = [
    path("", include(router.urls))
]
