import uuid

from django.db import models

from apps.profiles.models import Profile
from apps.products.models import ProductWithAmount


class Place(models.Model):
    name = models.CharField(max_length=300)
    members = models.ManyToManyField(Profile, related_name='places', blank=True, through='PlaceMember')

    def __str__(self):
        return '%s' % (self.name)


class InventoryItem(ProductWithAmount):
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='inventory')


class PlaceMember(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    member = models.ForeignKey(Profile, on_delete=models.CASCADE)
    is_the_default_one = models.BooleanField(default=False)


class Purchase(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)


class PurchaseItem(ProductWithAmount):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='items')
