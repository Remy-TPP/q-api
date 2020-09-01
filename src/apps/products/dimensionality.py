from django.db import models


class Dimensionality(models.TextChoices):
    UNIT = '[unit]'
    VOLUME = '[volume]', '[length] ** 3'
    MASS = '[mass]'
