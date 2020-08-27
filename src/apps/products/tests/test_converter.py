from django.test import TestCase
from apps.products.utils import convert_to_correct_unit

from apps.products.models import Amount, Product, Unit
from apps.inventories.models import InventoryItem, Place


class ConverterTests(TestCase):
    fixtures = ['unit']

    def setUp(self):
        self.place = Place.objects.create()

        self.leche = Product.objects.create(
            name='Leche',
            density=1032
        )

        self.manzana = Product.objects.create(
            name='Manzana',
            avg_unit_weight=0.252
        )

    def test_convert_mass_with_density_to_volume(self):
        """ When converting 2064g to L with density=1032kg/m**3, should return 2L"""

        item = InventoryItem.objects.create(
            place=self.place,
            product=self.leche,
            quantity=5,
            unit=Unit.objects.get(short_name='L')
        )

        amount = Amount(unit=Unit.objects.get(short_name='g'), quantity=2064)

        obj, other = convert_to_correct_unit(item, amount)

        self.assertEqual(round(other.magnitude), 2)
        self.assertEqual(round((obj - other).magnitude), 3)

    def test_convert_volume_with_density_to_mass(self):
        """ When converting 0.4845L to kg with density=1032kg/m**3, should return 0.5kg"""

        item = InventoryItem.objects.create(
            place=self.place,
            product=self.leche,
            quantity=5,
            unit=Unit.objects.get(short_name='kg')
        )

        amount = Amount(unit=Unit.objects.get(short_name='L'), quantity=0.4845)

        obj, other = convert_to_correct_unit(item, amount)

        self.assertEqual(round(other.magnitude, 1), 0.5)
        self.assertEqual(round((obj - other).magnitude, 1), 4.5)

    def test_convert_mass_to_unit(self):
        """ When converting 2kg to unit with avg_unit_weight=0.252kg, should return ~8"""

        item = InventoryItem.objects.create(
            place=self.place,
            product=self.manzana,
            quantity=2,
            unit=Unit.objects.get(name='unit')
        )

        amount = Amount(unit=Unit.objects.get(short_name='kg'), quantity=2)

        obj, other = convert_to_correct_unit(item, amount)

        self.assertEqual(round(other.magnitude), 8)
        self.assertEqual(round((obj - other).magnitude), -6)

    def test_convert_unit_to_mass(self):
        """ When converting 1unit to g with avg_unit_weight=0.252kg, should return 252g"""

        item = InventoryItem.objects.create(
            place=self.place,
            product=self.manzana,
            quantity=1000,
            unit=Unit.objects.get(short_name='g')
        )

        amount = Amount(unit=Unit.objects.get(name='unit'), quantity=1)

        obj, other = convert_to_correct_unit(item, amount)

        self.assertEqual(round(other.magnitude), 252)
        self.assertEqual(round((obj - other).magnitude), 748)
