from measurement.utils import guess


def sub_weights_with_units(weight_1, unit_1, weight_2, unit_2):
    """
    Returns the result of 'weight_1 - weight_2' in the same unit as 'unit_1'
    """
    # TODO: mejorarla para unidades, cucharadas, tazas, etc
    result = guess(weight_1, unit_1) - guess(weight_2, unit_2)
    return result.value
