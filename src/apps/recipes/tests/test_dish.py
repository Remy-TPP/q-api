from django.test import TestCase

from apps.recipes.models import Dish


class DishTests(TestCase):
    def setUp(self):
        self.dish0 = Dish(name="The bestest dish")
        self.dish1 = Dish(name="Some meh dish", description="Anything else is better")

    def test_str_is_name(self):
        self.assertEqual(self.dish0.__str__(), self.dish0.name)
        self.assertEqual(self.dish1.__str__(), self.dish1.name)
