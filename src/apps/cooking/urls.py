from django.urls import path

from apps.cooking.views import hello_world, cook_recipe


urlpatterns = [
    path('hello', hello_world),
    path('cook_recipe', cook_recipe)
]
