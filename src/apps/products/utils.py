from measurement.utils import guess


def sub_quantities_with_units(quantity_1, unit_1, quantity_2, unit_2):
    """Returns the result of quantity_1 - quantity_2 in the same unit as unit_1."""
    # TODO: mejorarla para unidades, cucharadas, tazas, etc
    result = guess(quantity_1, unit_1) - guess(quantity_2, unit_2)
    return result.value
