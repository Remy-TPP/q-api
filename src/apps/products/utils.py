from common.utils import Q_


def convert_to_correct_unit(obj, other):
    obj_amount = Q_(obj.quantity, obj.unit.short_name)
    other_amount = Q_(other.quantity, other.unit.short_name)

    other_amount_dim = other_amount.dimensionality
    obj_amount_dim = obj_amount.dimensionality

    if (obj_amount_dim != other_amount_dim):
        if (str(other_amount_dim) == '[mass]'
                and obj_amount_dim == '[length] ** 3'
                and obj.product.density is not None):
            other_amount = other_amount / Q_(obj.product.density, 'kg / (m ** 3)')

        elif (str(other_amount_dim) == '[length] ** 3'
              and obj_amount_dim == '[mass]'
              and obj.product.density is not None):
            other_amount = other_amount * Q_(obj.product.density, 'kg / (m ** 3)')

        elif (str(other_amount_dim) == '[unit]'
              and obj_amount_dim == '[mass]'
              and obj.product.avg_unit_weight is not None):
            other_amount = other_amount * Q_(obj.product.avg_unit_weight, 'kg')

        elif (str(other_amount_dim) == '[mass]'
              and obj_amount_dim == '[unit]'
              and obj.product.avg_unit_weight is not None):
            other_amount = other_amount / Q_(obj.product.avg_unit_weight, 'kg')

    return obj_amount, other_amount


def sub_quantities_with_units(obj, other):
    """Returns the result of obj.quantity - other.quantity in the same unit as obj.unit."""
    result = obj - other
    return result.magnitude


def add_quantities_with_units(obj, other):
    """Returns the result obj.quantity + other.quantity in the same unit as obj.unit."""
    result = obj + other
    return result.magnitude
