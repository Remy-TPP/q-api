from decimal import Decimal

from django.test import TestCase

from apps.products.models import Unit, Amount


class AmountTests(TestCase):
    fixtures = ['unit']

    def setUp(self):
        # TODO: would it be better to use Units independent from fixture?
        self.plain_unit = Unit.objects.get(name="unit")
        self.kg_unit = Unit.objects.get(short_name='kg')
        self.liter_unit = Unit.objects.get(short_name='L')
        self.cup_unit = Unit.objects.get(name='cup')

    def test_plain_unit_has_empty_short_name(self):
        a1 = Amount(unit=self.plain_unit, quantity=Decimal('3'))

        self.assertEqual(a1.__str__(), '3')

    def test_unplain_units_have_its_short_name(self):
        a2 = Amount(unit=self.kg_unit, quantity=Decimal('3.14'))
        a3 = Amount(unit=self.liter_unit, quantity=Decimal('2.718'))

        self.assertIn(self.plain_unit.short_name, a2.__str__())
        self.assertIn(self.liter_unit.short_name, a3.__str__())

    def test_default_unit_is_plain(self):
        a4 = Amount(quantity=Decimal('42'))

        self.assertEqual(a4.unit, self.plain_unit)

    def test_unshortened_units_have_pluralized_name_when_appropriate(self):
        a5 = Amount(unit=self.cup_unit, quantity=Decimal('108'))
        a6 = Amount(unit=self.cup_unit, quantity=Decimal('1.000'))
        a7 = Amount(unit=self.cup_unit, quantity=Decimal('0.025'))
        a8 = Amount(unit=self.cup_unit, quantity=Decimal('1'))

        self.assertIn('cups', a5.__str__())
        self.assertIn('cup',  a6.__str__())
        self.assertIn('cups', a7.__str__())
        self.assertIn('cup',  a8.__str__())
