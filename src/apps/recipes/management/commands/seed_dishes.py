"""python manage.py seed_dishes"""
# import sys
import csv
from enum import Enum

from django.core.management.base import BaseCommand

from apps.recipes.models import Dish, Recipe, RecipeInstructions, DishLabel
from .dish_parser import DishParser


# def print(s):
#     # Overwrite standard print for command use
#     sys.stdout.write(s)


class Mode(Enum):
    # Clear all data
    CLEAR = 'clear'
    # Add seed as new rows
    APPEND = 'append'
    # Clear all data and reseed
    REFRESH = 'refresh'


class Command(BaseCommand):
    help = 'seed database for testing and development'

    def add_arguments(self, parser):
        parser.add_argument('--mode', type=str, help='Mode', choices=[m.value for m in Mode])
        parser.add_argument('--file', type=str, help='CSV seed')
        parser.add_argument('--clean', type=str, default=None, help='Output cleaned CSV with only accepted dishes')
        parser.add_argument('-n', type=int, default=100, help='Amount of rows')

    def handle(self, *args, **options):
        print('seeding data...')
        nrows = run_seed(options['mode'], options['file'], options['n'], options['clean'])
        print(f'done. {nrows} rows added.')


def clear_data():
    """Delete all Dishes, Recipes, RecipeInstructions and DishLabels.

    Note it does not delete Products."""
    Dish.objects.all().delete()
    Recipe.objects.all().delete()
    # If Recipe's delete was well implemented this next line shouldn't be necessary
    RecipeInstructions.objects.all().delete()
    DishLabel.objects.all().delete()


def run_seed(mode, seed_file, n, clean=None):
    """Seed database with CSV file based on mode."""
    if mode != Mode.APPEND.value:
        clear_data()

    if mode == Mode.CLEAR.value:
        return 0

    dish_parser = DishParser()

    with open(seed_file) as csvf:
        # Implicit newline=None means line endings (e.g. '\r\n') are translated into '\n', which is desired
        reader = csv.DictReader(csvf, delimiter=',')

        if clean:
            outf = open(clean, 'w', newline='')
            writer = csv.DictWriter(outf, fieldnames=reader.fieldnames, delimiter=',')
            writer.writeheader()

        # Stop after the first N rows
        for j in range(n):
            if not (row := next(reader, None)):
                break

            added = dish_parser.parse_and_create_dish(row)

            if added and clean:
                writer.writerow(row)

            print(f'[{dish_parser.rows_added_count}/{j+1}]')

        if clean:
            outf.close()

    print('\nWords not recognized as conventional units and treated as product names\n-----')
    for unn in sorted(dish_parser.unrecognized_unit_names().items(), key=lambda x: x[0]):
        print(f'{unn[0]}: {unn[1]}')
    print('')

    return dish_parser.rows_added_count
