from django.urls import path

from apps.cooking.views import cook_recipe


urlpatterns = [
    path('cook_recipe', cook_recipe, name='cook-recipe'),
]
