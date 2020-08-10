from django.db import models

from apps.profiles.models import Profile
from apps.products.models import Product, Amount


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

    def reduce_amount(self, amount):
        must_be_deleted = self.amount - amount
        if must_be_deleted:
            self.delete()

    def add_amount(self, amount):
        _ = self.amount + amount


class Place(models.Model):
    name = models.CharField(max_length=300)
    members = models.ManyToManyField(Profile, related_name='places', blank=True, through='PlaceMember')
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, blank=True)

    def __str__(self):
        return '%s' % (self.name)


class PlaceMember(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    member = models.ForeignKey(Profile, on_delete=models.CASCADE)
    is_the_default_one = models.BooleanField(default=False)
