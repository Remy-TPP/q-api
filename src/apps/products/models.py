from django.db import models


class Unit(models.Model):
    name = models.CharField(max_length=50, unique=True)
    short_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Amount(models.Model):
    quantity = models.DecimalField(decimal_places=5)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.displayable_quantity()} {self.unit.short_name}'

    def displayable_quantity(self):
        return round(self.quantity, 2)


class Product(models.Model):
    name = models.CharField(max_length=300, unique=True)

    def __str__(self):
        return self.name
