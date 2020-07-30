from django.db import models

from apps.profiles.models import Profile
from apps.recipes.models import Product, Amount


class Inventory(models.Model):
    name = models.CharField(max_length=300)
    products = models.ManyToManyField(Product, through='InventoryItem')

    def __str__(self):
        return '%s' % (self.name)


class InventoryItem(models.Model):
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.OneToOneField(Amount, on_delete=models.CASCADE)

    def __str__(self):
        return '%s of %s' % (self.amount, self.product)


class Place(models.Model):
    name = models.CharField(max_length=300)
    members = models.ManyToManyField(Profile, related_name='places', blank=True)
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, blank=True)

    def __str__(self):
        return '%s' % (self.name)
