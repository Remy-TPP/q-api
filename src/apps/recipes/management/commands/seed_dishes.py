"""python manage.py seed_dishes"""
import csv

from django.core.management.base import BaseCommand

from apps.recipes.models import Dish


# CLear all data
MODE_CLEAR = 'clear'
# Clear all data and reseed
MODE_REFRESH = 'refresh'


class Command(BaseCommand):
    help = 'seed database for testing and development'

    def add_arguments(self, parser):
        parser.add_argument('--mode', type=str, help='Mode')
        parser.add_argument('--file', type=str, help='CSV seed')
        parser.add_argument('--n', type=int, default=100, help='Amount of rows')

    def handle(self, *args, **options):
        self.stdout.write('seeding data...')
        run_seed(self, options['mode'], options['file'], options['n'])
        self.stdout.write('done.')


def clear_data():
    """Deletes all Dishes (and by cascade its Recipes)."""
    Dish.objects.all().delete()


def run_seed(self, mode, seed_file, n):
    """Seed database with CSV file based on mode."""
    clear_data()
    if mode == MODE_CLEAR:
        return

    with open(seed_file) as csvf:
        reader = csv.DictReader(csvf, delimiter=',')
        # Only grab the first N rows
        for i in range(n):
            row = next(reader, None)
            if not row:
                break
            Dish.objects.create(
                title=row['title'],
                description=row['description'],
                tags=row['tags']
            )
            # TODO: row['recipes'], slug, assets
