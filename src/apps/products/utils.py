from pint import UnitRegistry
from django.conf import settings

ureg = UnitRegistry()
ureg.load_definitions(settings.BASE_DIR + '/common/unit_definitions/units.txt')
Q_ = ureg.Quantity


def sub_quantities_with_units(quantity_1, unit_1, quantity_2, unit_2):
    """Returns the result of quantity_1 - quantity_2 in the same unit as unit_1."""
    # TODO: mejorarla para unidades, cucharadas, tazas, etc
    result = Q_(quantity_1, unit_1) - Q_(quantity_2, unit_2)
    return result.magnitude


def add_quantities_with_units(quantity_1, unit_1, quantity_2, unit_2):
    """Returns the result of quantity_1 - quantity_2 in the same unit as unit_1."""
    # TODO: mejorarla para unidades, cucharadas, tazas, etc
    result = Q_(quantity_1, unit_1) + Q_(quantity_2, unit_2)
    return result.magnitude
