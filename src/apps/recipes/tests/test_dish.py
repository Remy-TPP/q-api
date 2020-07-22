from django.test import TestCase

from apps.recipes.models import Dish


class DishTests(TestCase):
    def setUp(self):
        self.d0 = Dish(name="The bestest dish")
        self.d1 = Dish(name="Some meh dish", description="Anything else is better")

    def test_str_is_name(self):
        self.assertEqual(self.d0.__str__(), self.d0.name)
        self.assertEqual(self.d1.__str__(), self.d1.name)
