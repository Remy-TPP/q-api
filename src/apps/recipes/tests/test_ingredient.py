from decimal import Decimal

from django.test import TestCase

from apps.products.models import Product, Amount
from apps.recipes.models import Ingredient, Dish, Recipe


class IngredientTests(TestCase):
    def setUp(self):
        # TODO: should do this with mock objects?
        dish0 = Dish(name="The bestest dish")
        rec0 = Recipe(dish=dish0, title="Some awesome recipe")
        self.pr0 = Product(name="Harina 0000")
        self.pr1 = Product(name="Manzana")
        self.am0 = Amount(quantity=Decimal('10.01'))
        self.am1 = Amount(quantity=Decimal('5'))
        self.ing0 = Ingredient(product=self.pr0, recipe=rec0, quantity=Decimal('10.01'))
        self.ing1 = Ingredient(product=self.pr1, recipe=rec0, quantity=Decimal('5'))

    def test_str_includes_amount_and_product(self):
        self.assertIn(self.am0.__str__(), self.ing0.__str__())
        self.assertIn(self.pr0.__str__(), self.ing0.__str__())
        self.assertIn(self.am1.__str__(), self.ing1.__str__())
        self.assertIn(self.pr1.__str__(), self.ing1.__str__())
