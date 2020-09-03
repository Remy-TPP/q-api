"""python manage.py seed_dishes"""
# import sys
import csv
from enum import Enum

from django.core.management.base import BaseCommand

from apps.recipes.models import Dish, Recipe, DishLabel
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
        parser.add_argument('-n', type=int, default=100, help='Amount of rows')

    def handle(self, *args, **options):
        print('seeding data...')
        nrows = run_seed(self, options['mode'], options['file'], options['n'])
        print(f'done. {nrows} rows added.')


def clear_data():
    """Delete all Dishes, Recipes and DishLabels."""
    Dish.objects.all().delete()
    Recipe.objects.all().delete()
    DishLabel.objects.all().delete()


def run_seed(self, mode, seed_file, n):
    """Seed database with CSV file based on mode."""
    if mode != Mode.APPEND.value:
        clear_data()

    if mode == Mode.CLEAR.value:
        return 0

    dish_parser = DishParser()

    with open(seed_file) as csvf:
        reader = csv.DictReader(csvf, delimiter=',')
        # Only grab the first N rows
        for j in range(n):
            if not (row := next(reader, None)):
                break
            dish_parser.parse_and_create_dish(row)
            print(f'[{dish_parser.rows_added_count}/{j+1}]')

    print('\nWords not recognized as conventional units and treated as product names\n-----')
    for unn in sorted(dish_parser.unrecognized_unit_names().items(), key=lambda x: x[0]):
        print(f'{unn[0]}: {unn[1]}')
    print('')

    return dish_parser.rows_added_count
