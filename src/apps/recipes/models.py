from django.db import models

from apps.recipes.utils import sub_weights_with_units


class Unit(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return '%s' % (self.name)


class Amount(models.Model):
    # TODO: maybe DecimalField would be better?
    weight = models.FloatField()
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)

    def __str__(self):
        return f'{round(self.weight, 2), str(self.unit)}'

    def __sub__(self, other):
        """
        Makes the logic to decrease the amount.
        Returns True or False whether the amount is not longer usable or it is.
        """
        weight_result = sub_weights_with_units(self.weight, self.unit.name, other.weight, other.unit.name)
        self.weight = weight_result
        self.save()
        return weight_result <= 0


class Product(models.Model):
    name = models.CharField(max_length=300, unique=True)

    def __str__(self):
        return '%s' % (self.name)


class Ingredient(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.ForeignKey(Amount, on_delete=models.CASCADE)
    parent = models.ForeignKey("self",
                               blank=True,
                               null=True,
                               related_name='substitutions',
                               on_delete=models.CASCADE)

    def __str__(self):
        return '%s of %s' % (self.amount, self.product)


class Recipe(models.Model):
    title = models.CharField(max_length=300)
    description = models.CharField(max_length=300)
    image = models.ImageField(upload_to='images/%Y-%m-%d', null=True)
    ingredients = models.ManyToManyField(Ingredient, related_name='recipes')

    def __str__(self):
        return '%s' % (self.title)
