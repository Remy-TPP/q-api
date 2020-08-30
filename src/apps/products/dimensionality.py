from django.db import models


class Dimensionality(models.TextChoices):
    UNIT = '[unit]'
    VOLUME = '[volume]'
    MASS = '[mass]'
