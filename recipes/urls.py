from django.urls import path
from .views import *

urlpatterns = [
	path('recipes/', Recipes.as_view(), name='recipe-list'),
	path('recipes/<int:pk>/', Recipe.as_view(), name='recipe-detail'),
]