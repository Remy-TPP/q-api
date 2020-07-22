from decimal import Decimal

from django.test import TestCase

from apps.products.models import Product, Amount
from apps.recipes.models import Ingredient, Dish, Recipe


class IngredientTests(TestCase):
    def setUp(self):
        # TODO: should do this with mock objects?
        d0 = Dish(name="The bestest dish")
        r0 = Recipe(dish=d0, title="Some awesome recipe")
        self.p0 = Product(name="Harina 0000")
        self.p1 = Product(name="Manzana")
        self.a0 = Amount(quantity=Decimal('10.01'))
        self.a1 = Amount(quantity=Decimal('5'))
        self.i0 = Ingredient(product=self.p0, recipe=r0, amount=self.a0)
        self.i1 = Ingredient(product=self.p1, recipe=r0, amount=self.a1)

    def test_str_includes_amount_and_product(self):
        self.assertIn(self.a0.__str__(), self.i0.__str__())
        self.assertIn(self.p0.__str__(), self.i0.__str__())
        self.assertIn(self.a1.__str__(), self.i1.__str__())
        self.assertIn(self.p1.__str__(), self.i1.__str__())
