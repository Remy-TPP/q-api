from django.urls import include, path
from rest_framework.routers import SimpleRouter

from apps.recipes.views import DishCategoryViewSet, DishLabelViewSet, RecipeViewSet, DishViewSet


router = SimpleRouter()

router.register(r'dishcategories', DishCategoryViewSet)            # dishcategories/
router.register(r'dishlabels', DishLabelViewSet)                   # dishlabels/
# router.register(r'ingredients', IngredientViewSet)                 # ingredients/      (not needed)
router.register(r'recipes', RecipeViewSet)                         # recipes/
router.register(r'dishes', DishViewSet)                            # dishes/


urlpatterns = [
    path('', include(router.urls)),
]
