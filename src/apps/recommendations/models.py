from django.db import models

from apps.profiles.models import Profile
from apps.recipes.models import Recipe


# TODO: remove
class Recommendation(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=False, null=False)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, blank=False, null=False)
    score = models.DecimalField(blank=True, null=True, decimal_places=10, max_digits=12)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['profile', 'recipe'], name='unique_recommendation')
        ]


class RecipeRecommendation(models.Model):
    # profile = models.ForeignKey(Profile, blank=False, null=False, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, blank=False, null=False, on_delete=models.CASCADE)
    rating = models.DecimalField(max_digits=4, decimal_places=2, blank=False, null=False)
    rating_is_real = models.BooleanField()

    class Meta:
        managed = False
        # constraints = [
        #     models.UniqueConstraint(fields=['profile', 'recipe'], name='unique_recommendation')
        # ]

    def __str__(self):
        return f'For recipe {self.recipe} rating {self.rating} ({"real" if self.rating_is_real else "generated"})'

    def save(self, *args, **kwargs):
        # Never saving this model, just using it as a class with Django powers
        pass
