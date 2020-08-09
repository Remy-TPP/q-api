from django.test import TestCase

from apps.products.models import Unit


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
