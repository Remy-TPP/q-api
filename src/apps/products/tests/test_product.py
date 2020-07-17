from django.test import TestCase

from apps.products.models import Product


class ProductTests(TestCase):
    def setUp(self):
        self.p1 = Product(name="Harina 0000")
        self.p2 = Product(name="Choclo en grano")
        self.p3 = Product(name="Porotos rojos")

    def test_str_is_name(self):
        self.assertEqual(self.p1.__str__(), "Harina 0000")
        self.assertEqual(self.p2.__str__(), "Choclo en grano")
        self.assertEqual(self.p3.__str__(), "Porotos rojos")
