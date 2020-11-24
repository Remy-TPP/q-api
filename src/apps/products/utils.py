from common.utils import Q_

from apps.products.dimensionality import Dimensionality


def convert_to_correct_unit(obj, other):
    """Receive ProductWithAmount and Amount/ProductWithAmount"""

    obj_amount = Q_(obj.quantity, obj.unit.name)
    other_amount = Q_(other.quantity, other.unit.name)

    other_amount_dim = other_amount.dimensionality
    obj_amount_dim = obj_amount.dimensionality

    if (obj_amount_dim != other_amount_dim):
        if (str(other_amount_dim) == Dimensionality.MASS
                and str(obj_amount_dim) == Dimensionality.VOLUME.label
                and obj.product.density is not None):
            other_amount = other_amount / Q_(obj.product.density, 'kg / (m ** 3)')

        elif (str(other_amount_dim) == Dimensionality.VOLUME.label
              and str(obj_amount_dim) == Dimensionality.MASS
              and obj.product.density is not None):
            other_amount = other_amount * Q_(obj.product.density, 'kg / (m ** 3)')

        elif (str(other_amount_dim) == Dimensionality.UNIT
              and str(obj_amount_dim) == Dimensionality.MASS
              and obj.product.avg_unit_weight is not None):
            other_amount = Q_((other_amount * Q_(obj.product.avg_unit_weight, 'kg')).magnitude, 'kg')

        elif (str(other_amount_dim) == Dimensionality.MASS
              and str(obj_amount_dim) == Dimensionality.UNIT
              and obj.product.avg_unit_weight is not None):
            other_amount = Q_((other_amount / Q_(obj.product.avg_unit_weight, 'kg')).magnitude, 'unit')

        elif (str(other_amount_dim) == Dimensionality.UNIT
              and str(obj_amount_dim) == Dimensionality.VOLUME.label
              and obj.product.avg_unit_volume is not None):
            other_amount = Q_((other_amount * Q_(obj.product.avg_unit_volume, 'L')).magnitude, 'L')

        elif (str(other_amount_dim) == Dimensionality.VOLUME.label
              and str(obj_amount_dim) == Dimensionality.UNIT
              and obj.product.avg_unit_volume is not None):
            other_amount = Q_((other_amount / Q_(obj.product.avg_unit_volume, 'L')).magnitude, 'unit')

    return obj_amount, other_amount.to(obj_amount.units)


def sub_quantities_with_units(obj, other):
    """Returns the result of obj.quantity - other.quantity in the same unit as obj.unit."""
    result = obj - other
    return result.magnitude


def add_quantities_with_units(obj, other):
    """Returns the result obj.quantity + other.quantity in the same unit as obj.unit."""
    result = obj + other
    return result.magnitude
