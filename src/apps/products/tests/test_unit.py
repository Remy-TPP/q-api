from django.test import TestCase
from pint import errors
from common.utils import Q_

from apps.products.models import Unit
from apps.products.utils import add_quantities_with_units, sub_quantities_with_units


class UnitTests(TestCase):
    fixtures = ['unit']

    def setUp(self):
        # TODO: alternatively could get a random sample of the units? Test all?
        self.test_units = [
            Unit.objects.get(short_name='kg'),
            Unit.objects.get(short_name='L'),
            Unit.objects.get(name='cup'),
            Unit.objects.get(short_name='mL'),
        ]

    def test_str_is_name(self):
        for test_unit in self.test_units:
            self.assertEqual(test_unit.__str__(), test_unit.name)

    def test_pluralized_is_name_ending_in_s(self):
        for test_unit in self.test_units:
            self.assertRegex(test_unit.pluralized_name,
                             rf'^{test_unit.name}\w*s$')


class UnitUtilsTests(TestCase):
    def test_add_quantities_cup_and_liter(self):
        result = add_quantities_with_units(Q_(1, 'liter'), Q_(1, 'cup'))
        self.assertEqual(result, 1.25)

    def test_add_quantities_liter_and_cup(self):
        # TODO: ver el tema del round
        result = add_quantities_with_units(Q_(2, 'cup'), Q_(3, 'l'))
        self.assertEqual(round(result), 14)

    def test_add_quantities_unit_and_unit(self):
        result = add_quantities_with_units(Q_(5, 'u'), Q_(3, 'unit'))
        self.assertEqual(result, 8)

    def test_sub_quantities_tablespoon_with_teaspoon(self):
        result = sub_quantities_with_units(Q_(1, 'tablespoon'), Q_(1, 'teaspoon'))
        self.assertEqual(result, 2/3)

    def test_sub_quantities_tablespoon_with_unit_error(self):
        with self.assertRaises(errors.DimensionalityError):
            _ = sub_quantities_with_units(Q_(1, 'tablespoon'), Q_(1, 'unit'))
