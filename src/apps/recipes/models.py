from django.db import models

from apps.products.models import Amount, Product


class Recipe(models.Model):
    title = models.CharField(max_length=300)
    description = models.TextField()
    image = models.ImageField(upload_to='images/recipes/%Y-%m-%d', null=True)
    ingredients = models.ManyToManyField(Product, through='Ingredient')

    def __str__(self):
        return self.title


class Ingredient(models.Model):
    # TODO: add related_name='+' to product's FK?
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, null=True)
    amount = models.OneToOneField(Amount, on_delete=models.CASCADE)
    # substitutions = models.ForeignKey('self',
    #                                   blank=True,
    #                                   null=True,
    #                                   related_name='substitutions',
    #                                   on_delete=models.CASCADE)

    def __str__(self):
        # TODO: make more human (e.g. '2 apples' instead of '2.00 of apple')
        return f'{self.amount} of {self.product}'
