from django.db import models


class Unit(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return '%s' % (self.name)


class Amount(models.Model):
    weight = models.FloatField()
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)

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
