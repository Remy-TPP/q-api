from django.db import models
from django_better_admin_arrayfield.models.fields import ArrayField

from apps.products.models import Product, ProductWithAmount


class DishCategory(models.Model):
    name = models.CharField(max_length=60)
    description = models.CharField(max_length=300)

    class Meta:
        verbose_name_plural = "dish categories"

    def __str__(self):
        return self.name


class DishLabel(models.Model):
    name = models.CharField(max_length=60)
    image = models.ImageField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "dish labels"

    def __str__(self):
        return self.name


class Dish(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=300)
    description = models.TextField()
    # TODO: `related_name='+'` for either of categories or labels?
    categories = models.ManyToManyField(DishCategory, blank=True)
    labels = models.ManyToManyField(DishLabel, blank=True)

    class Meta:
        verbose_name_plural = "dishes"

    def __str__(self):
        return self.name


class RecipeInstructions(models.Model):
    steps = ArrayField(models.TextField(), default=list)

    class Meta:
        verbose_name_plural = "recipe instructions"

    def __str__(self):
        """Example output: '[8 steps]'"""
        return f"[{len(self.steps)} step{'s' if len(self.steps) != 1 else ''}]"

    @classmethod
    def default(cls):
        return cls.objects.create().pk

    @property
    def displayable_steps(self):
        """Example output: '1. Foo\n\n\n2. Bar\n\n\n3. Baz'"""
        return '\n\n\n'.join([f'{i+1}. {t}' for i, t in enumerate(self.steps)])


class Recipe(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    dish = models.ForeignKey(Dish, on_delete=models.SET_NULL, null=True, related_name='recipes')
    title = models.CharField(max_length=300, blank=True)
    description = models.TextField()
    image = models.ImageField(upload_to='images/recipes', null=True, blank=True)
    ingredients = models.ManyToManyField(Product, through='Ingredient')
    # TODO: if Recipe is deleted, so should its instructions
    instructions = models.OneToOneField(RecipeInstructions,
                                        default=RecipeInstructions.default,
                                        on_delete=models.CASCADE)

    def __str__(self):
        return self.title if self.title else self.dish.name


class Ingredient(ProductWithAmount):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    notes = models.CharField(max_length=300, blank=True)
    section = models.CharField(max_length=100, blank=True)
