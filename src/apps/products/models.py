from django.db import models

from apps.products.dimensionality import Dimensionality
from apps.products.utils import (sub_quantities_with_units,
                                 add_quantities_with_units,
                                 convert_to_correct_unit)


class Unit(models.Model):
    name = models.CharField(max_length=50, unique=True)
    short_name = models.CharField(max_length=50, unique=True, null=True)
    dimensionality = models.CharField(max_length=50, default=Dimensionality.UNIT)

    def __str__(self):
        return self.name

    # TODO: revisit later
    @property
    def pluralized_name(self):
        return self.name + 's'


class Amount(models.Model):
    quantity = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.displayable_quantity}{self.displayable_unit}'

    def __sub__(self, other):
        """Decrease own quantity with other's.

        Returns True if this amount is no longer usable.
        """
        obj, other = convert_to_correct_unit(self, other)

        quantity_result = sub_quantities_with_units(
            obj,
            other
        )
        self.quantity = quantity_result
        return quantity_result <= 0

    def __add__(self, other):
        """Add own quantity with other's.
        """
        obj, other = convert_to_correct_unit(self, other)

        quantity_result = add_quantities_with_units(
            obj,
            other
        )
        self.quantity = quantity_result

    @property
    def displayable_unit(self):
        if self.unit is not None:
            if self.unit.short_name is None:
                return f' {self.unit.name if self.quantity == 1.0 else self.unit.pluralized_name}'

            if self.unit.short_name == '':
                return ''

            return f' {self.unit.short_name}'
        return ''

    @property
    def displayable_quantity(self):
        """Returns string of quantity with at most 2 decimals."""
        return f'{self.quantity:.2f}'.rstrip('0').rstrip('.') if self.quantity else ''


class Product(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=300, unique=True)
    available_dimensionalities = models.CharField(
        max_length=300,
        default=Dimensionality.UNIT
    )  # split by comma
    density = models.DecimalField(max_digits=12, decimal_places=5, null=True, blank=True)  # kg / m ** 3
    avg_unit_weight = models.DecimalField(max_digits=12, decimal_places=5, null=True, blank=True)  # kg
    avg_unit_volume = models.DecimalField(max_digits=12, decimal_places=5, null=True, blank=True)  # L

    def __str__(self):
        return self.name


class ProductWithAmount(Amount):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.displayable_quantity}{self.displayable_unit} {self.product}'

    def add_amount(self, other_amount):
        _ = self + other_amount
        self.save()

    def reduce_amount(self, amount):
        must_be_deleted = self - amount
        if must_be_deleted:
            self.delete()
        else:
            self.save()
