from unittest import TestCase

from apps.profiles.models import Profile
from apps.recipes.models import Recipe, Ingredient
from apps.recommendations.utils import ComparableInventory


# TODO: written for manual testing with preloaded db; for general use should create resources in setUp()
class ComparableInventoryTest(TestCase):
    def setUp(self):
        prof = Profile.objects.get(pk=3)
        place = prof.places.first()
        inv = place.inventory.all().prefetch_related('product', 'unit')

        try:
            print('creating')
            print(f'---- {self.inv}')
            self.inv.print_inventory(product_id=329)
        except AttributeError:
            pass
        self.inv = ComparableInventory(inv)
        self.inv.print_inventory(product_id=329)

    def tearDown(self):
        print('destroying')
        self.inv.destroy()
        self.inv.print_inventory()
        self.inv = None
        print('destroyed')

    def test_print(self):
        self.inv.print_inventory(product_id=329)

    def test_substract_ingredient(self):
        # Product ID 329: pepino
        ing = Ingredient.objects.filter(product_id=329)[0]
        print(ing)

        self.inv.print_inventory(product_id=329)

        self.inv.substract(ing)

        print(self.inv.inventory.get(329))
        self.inv.print_inventory(product_id=329)

    def test_reset(self):
        ing = Ingredient.objects.filter(product_id=329)[0]

        self.assertEqual(self.inv.get(329).quantity, 3)
        self.inv.substract(ing)
        self.assertEqual(self.inv.get(329).quantity, 2)
        self.inv.substract(ing)
        self.assertEqual(self.inv.get(329).quantity, 1)

        self.inv.reset()
        self.assertEqual(self.inv.get(329).quantity, 3)

    def test_can_make_recipe(self):
        # Shouldn't be able to do this
        recipe1 = Recipe.objects.get(pk=313)
        self.assertFalse(self.inv.can_make(recipe1))

        # Should be able to make this one
        recipe2 = Recipe.objects.get(pk=291)
        self.assertTrue(self.inv.can_make(recipe2))

    def test_can_make_multiple_times(self):
        recipe = Recipe.objects.get(pk=291)
        self.assertTrue(self.inv.can_make(recipe))
        self.assertTrue(self.inv.can_make(recipe))
        self.assertTrue(self.inv.can_make(recipe))
