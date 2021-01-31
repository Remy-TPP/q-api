from django.db import models

from apps.recipes.models import Recipe


class RecipeRecommendation(models.Model):
    recipe = models.ForeignKey(Recipe, blank=False, null=False, on_delete=models.CASCADE)
    rating = models.DecimalField(max_digits=5, decimal_places=3, blank=False, null=False)
    rating_is_real = models.BooleanField()

    class Meta:
        managed = False

    def __str__(self):
        return f'For recipe {self.recipe} rating {self.rating} ({"real" if self.rating_is_real else "generated"})'

    def save(self, *args, **kwargs):
        # Never saving this model, just using it as a class with Django powers
        pass
