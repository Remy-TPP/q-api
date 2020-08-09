from django.contrib import admin

from apps.recipes.models import DishCategory, DishLabel, Dish, Recipe


admin.site.register(DishCategory)
admin.site.register(DishLabel)
admin.site.register(Dish)
admin.site.register(Recipe)
