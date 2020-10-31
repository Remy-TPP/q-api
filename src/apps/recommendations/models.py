from django.db import models

from apps.profiles.models import Profile
from apps.recipes.models import Recipe


class Recommendation(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=False, null=False)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, blank=False, null=False)
    score = models.DecimalField(blank=True, null=True, decimal_places=10, max_digits=12)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['profile', 'recipe'], name='unique_recommendation')
        ]
