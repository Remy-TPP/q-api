from copy import deepcopy

from pint import errors as pint_errors

from apps.products.utils import (convert_to_correct_unit,
                                 sub_quantities_with_units,
                                 add_quantities_with_units,
                                )


class NotEnoughError(RuntimeError):
    pass


class ComparableAmount:
    quantity = 0
    unit = None

    def __init__(self, quantity=0, unit=None, product=None):
        self.quantity = quantity
        self.unit = unit
        self.product = product

    def __str__(self):
        return f'{self.quantity} {self.unit}'

    def substract(self, other):
        """Decrease own quantity with other's."""
        self_qu, other_qu = convert_to_correct_unit(self, other)
        return sub_quantities_with_units(self_qu, other_qu)

    def __sub__(self, other):
        self.quantity = self.substract(other)
        return self.quantity

    def add(self, other):
        """Incrase own quantity with other's."""
        self_qu, other_qu = convert_to_correct_unit(self, other)
        return add_quantities_with_units(self_qu, other_qu)

    def __add__(self, other):
        self.quantity = self.add(other)
        return self.quantity


class ComparableInventory:
    def __init__(self, inventory_items):
        self.base_inventory = dict()

        # store each inventory item, adding to existing if already in it
        for item in inventory_items:
            current = self.base_inventory.get(item.product.id, None)
            addition = ComparableAmount(quantity=item.quantity, unit=item.unit, product=item.product)
            if current is None:
                self.base_inventory[item.product.id] = addition
            else:
                _ = current + addition

        # initialize inventory
        self.inventory = deepcopy(self.base_inventory)

    def destroy(self):
        self.inventory = None
        self.base_inventory = None

    def reset(self):
        for product_id, amount in self.base_inventory.items():
            self.inventory[product_id].quantity = amount.quantity

    def get(self, product_id: int) -> ComparableAmount:
        return self.inventory.get(product_id)

    def print_inventory(self, product_id=None):
        if not self.inventory:
            print('no inventory')
            return
        for prod_id, amount in self.inventory.items():
            if not product_id or prod_id == product_id:
                print(f'For {prod_id}, amount is {amount}')

    def substract(self, ingredient):
        amount = ComparableAmount(quantity=ingredient.quantity, unit=ingredient.unit, product=ingredient.product)
        current = self.inventory.get(ingredient.product_id, None)
        if current is None:
            raise NotEnoughError
        remaining = current - amount
        if remaining < 0:
            raise NotEnoughError

    def __sub__(self, ingredient):
        return self.substract(ingredient)

    def can_make(self, recipe):
        ingredients = recipe.ingredient_set.all()

        try:
            for ingr in ingredients:
                if ingr.quantity:
                    self.substract(ingr)
                else:
                    # if non-quantified, just check it's in inventory
                    _ = self.inventory[ingr.product_id]
        except (NotEnoughError, pint_errors.DimensionalityError, KeyError):
            self.reset()
            return False

        return True
