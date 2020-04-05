from django.urls import path
from .views import *

urlpatterns = [
	path('recipes/', Recipes.as_view(), name='recipe-list'),
	path('recipes/<int:pk>/', Recipe.as_view(), name='recipe-detail'),
    path('ingredients/', Ingredients.as_view(), name='ingredient-list'),
    path('ingredients/<int:pk>/', Ingredient.as_view(), name='ingredient-detail'),
    path('weights/', Weights.as_view(), name='weight-list'),
    path('weights/<int:pk>/', Weight.as_view(), name='weight-detail'),
]