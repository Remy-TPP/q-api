from django.test import TestCase

from apps.recipes.models import Dish, Recipe


class RecipeTests(TestCase):
    def setUp(self):
        d = Dish(name="The bestest dish")
        self.rec0 = Recipe(dish=d, title="Some mediocre recipe")
        self.rec1 = Recipe(dish=d)

    def test_str_shows_correct_name(self):
        self.assertEqual(self.rec0.__str__(), "Some mediocre recipe")
        self.assertEqual(self.rec1.__str__(), "The bestest dish")
