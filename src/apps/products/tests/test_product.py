from django.test import TestCase

from apps.products.models import Product


class ProductTests(TestCase):
    def setUp(self):
        self.pr1 = Product(name="Harina 0000")
        self.pr2 = Product(name="Choclo en grano")
        self.pr3 = Product(name="Porotos rojos")

    def test_str_is_name(self):
        self.assertEqual(self.pr1.__str__(), "Harina 0000")
        self.assertEqual(self.pr2.__str__(), "Choclo en grano")
        self.assertEqual(self.pr3.__str__(), "Porotos rojos")
