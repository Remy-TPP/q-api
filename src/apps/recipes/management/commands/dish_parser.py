import re
# import sys
import ast
import unicodedata
from decimal import Decimal
from fractions import Fraction
from collections import defaultdict, namedtuple

from apps.products.models import Unit, Product
from apps.recipes.models import Dish, DishLabel, Recipe, RecipeInstructions, Ingredient


# def print(s):
#     # Overwrite standard print for command use
#     sys.stdout.write(s)


UNICODE_VULGAR_FRACTIONS = '¼½¾⅐⅑⅒⅓⅔⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞'

possible_units = [
    'unit: unit',
    'gram: g gram grams gramo gramos gr grs g. gr. grs.',
    'kilogram: kg kilogram kilograms kilo kilos kilogramo kilogramos kg.',
    'liter: L l liter liters litro litros l.',
    'milliliter: mL ml milliliter milliliters mililitro mililitros ml. cc cc.',
    'cup: cup cups taza tazas',
    ('teaspoon: tsp teaspoon teaspoons cucharita cucharitas cucharadita cucharaditas '
     'cdta cdita cditas cdta. cdtas. cdita. cditas.'),
    'tablespoon: Tbsp tbsp tablespoon tablespoons cuchara cucharas cucharada cucharadas cda cdas cds. cda. cdas.',
    'pound: lb pound pounds libra libras lb.',
    'ounce: oz ounce ounces onza onzas oz.',
]
# Map from possible unit names to their corresponding Unit object
units_mapping = {u: Unit.objects.get(name=uu[0])  # {..., 'gram': <Unit: gram>, 'grams': <Unit: gram>, ...}
                 for uu in map(lambda x: x.split(': '), possible_units)  # [..., ['g', 'gram grams...']. ...]
                 for u in uu[1].split()}  # ['gram', 'grams', ...]
default_unit = units_mapping['unit']
unrecognized_unit_names = defaultdict(int)


""" INGREDIENT PARSING """

IngredientTuple = namedtuple('Ingredient', 'quantity unit product remarks section')


def pretty_ingr(ingr):
    return f'[{ingr.quantity} {ingr.unit}] de [{ingr.product}]' + (f' ({ingr.remarks})' if ingr.remarks else '')


def parse_ingredient(ingr_line, section_name):
    """Parses typical ingredient line format: '<quantity> [<unit> of] <ingredient>[, <remarks>]/[ (<remarks>)]'.

    Returns IngredientTuple, with None for any N/A."""
    ingr_line = ingr_line.strip()
    quantity, unit, remarks = None, None, None

    # look for number at beginning of string
    if (quantity_match := re.match(rf'^\s*(?:([0-9{UNICODE_VULGAR_FRACTIONS}.,/]+)\s*)+', ingr_line)):
        quantity = Decimal()
        # convert each part to Decimal and get full quantity (e.g. '2 ½' => Decimal('2.5'))
        # TODO: parse decimal comma
        # TODO: parse integer next to vulgar fraction (e.g. 2½)
        for p in quantity_match.group().split():
            try:
                f = float(Fraction(p))
            except ValueError:
                f = unicodedata.numeric(p)
            quantity += Decimal(str(f))
        ingr_line = ingr_line[quantity_match.end():]

        unit = default_unit
        # look for possible unit name
        if unit_match := re.match(r'^\s*(?:de\s*)?([^\d\W]+\b\.?)\s*(de\b\s*)?', ingr_line, re.IGNORECASE):
            try:
                unit = units_mapping[unit_match.group(1).lower()]
                ingr_line = ingr_line[unit_match.end():]
            except KeyError:
                unrecognized_unit_names[unit_match.group(1).lower()] += 1

    # look for comment at string end, after comma or between parentheses, and grab first match
    if (remarks_match := re.search(r'\s*(?:,\s*(.*)|\((.*)\))\s*$', ingr_line)):
        remarks = next((x.strip(' .') for x in remarks_match.groups() if x), None)
        ingr_line = ingr_line[:remarks_match.start()]

    # whatever's left should be the product name
    product = ingr_line.lower().strip(' ⠀.')  # includes U+2800 ("braille pattern blank")

    section_name = section_name.strip(': ') if section_name else None

    return IngredientTuple(quantity=quantity, unit=unit, product=product, remarks=remarks, section=section_name)


def seems_like_ingredient(line):
    """Check whether `line` starts with number."""
    return bool(
        re.search(rf'^[0-9{UNICODE_VULGAR_FRACTIONS}]', line)
    )


def seems_like_section_name(line):
    """Check whether `line` starts with 'Para' or ends with ':', ignoring case and whitespace."""
    return bool(
        re.search(r'(^[^a-záéíóúü0-9]*para\b|:\s*$)', line, re.IGNORECASE)
    )


def parse_ingredient_list(raw_ingrs_list):
    print('\n--- Original ---\n')
    [print(line) for line in raw_ingrs_list]

    ingrs = []
    d = defaultdict(list)  # TODO: this structure is redundant against ingrs but easier to print

    first_lines = True
    next_is_section_title = False
    section = None

    # TODO: try to simplify logic
    for line in raw_ingrs_list:
        if line and first_lines and not seems_like_ingredient(line):
            # something at the beginning which doesn't look like an ingredient is probably a section name
            section = line
            next_is_section_title = False
        elif not line:
            # empty lines usually precede section names
            if first_lines:
                continue
            next_is_section_title = True
        elif (next_is_section_title and not seems_like_ingredient(line)) \
                or seems_like_section_name(line):
            section = line
            next_is_section_title = False
        elif not (parsed_ingr := parse_ingredient(line, section)):
            # if ingredient parsing fails, just ignore it
            continue
        else:
            # else we have a new ingredient
            d[section].append(parsed_ingr)
            ingrs.append(parsed_ingr)
        first_lines = False

    print('\n--- Parsed ---')
    for section_ingrs in d.items():
        print(f'\nSección: {section_ingrs[0]}')
        [print(f'  {pretty_ingr(ingr)}') for ingr in section_ingrs[1]]

    # TODO: should use sys.stdin?
    if not input('\nInput any character IF the parsing seems CORRECT >'):
        return None

    return ingrs


""" RECIPE PARSING """


def parse_and_create_recipe(raw_recipe, dish, assets):
    print(f"\n\n\n[{dish.name}] *{raw_recipe['name'].strip()}*")

    # First verify we get a nice parsing, otherwise skip the recipe
    if not (parsed_ingrs := parse_ingredient_list(raw_recipe['ingredients'])):
        return False

    # Now we can create the recipe and all of its ingredients
    recipe, newly_created = Recipe.objects.get_or_create(
        dish=dish,
        title=raw_recipe['name'].strip(),
        defaults={
            'description': f"Source: {raw_recipe['source'].strip()}\nVideo: {assets}",
            'instructions': RecipeInstructions.objects.create(steps=raw_recipe['steps']),
        },
    )
    if not newly_created:
        print("Recipe with this name for this dish already exists; won't create ingredients")
        return False

    # Create each ingredient
    for parsed_ingr in parsed_ingrs:
        product = Product.objects.get_or_create(name=parsed_ingr.product)[0]
        Ingredient.objects.create(
            recipe=recipe,
            product=product,
            quantity=parsed_ingr.quantity,
            unit=(parsed_ingr.unit if parsed_ingr.unit else default_unit),
            notes=(parsed_ingr.remarks if parsed_ingr.remarks else ''),
            section=(parsed_ingr.section if parsed_ingr.section else '')
        )

    return True


""" DISH PARSING """


class DishParser:

    def __init__(self):
        self.rows_added_count = 0

    def unrecognized_unit_names(self):
        return unrecognized_unit_names

    def parse_and_create_dish(self, row):
        dish, is_new = Dish.objects.get_or_create(
            name=row['title'].strip(),
            # If a dish already exists with that title, description won't be overwritten
            defaults={
                'description': row['description'].strip(),
            },
        )

        # row['recipes'] is a string which holds a Python list of dicts in a string
        recipes = ast.literal_eval(row['recipes'])
        if (not any([parse_and_create_recipe(recipe_dict, dish, row['assets'])
                     for recipe_dict in recipes])
                and is_new):
            # If no recipes were created for a newly created dish, delete it
            dish.delete()
            return False

        # row['tags'] is a string which holds a Python list of string tags
        for tag in ast.literal_eval(row['tags']):
            print(f'Tag: {tag.strip().lower()}')
            dish.labels.add(
                DishLabel.objects.get_or_create(name=tag.strip().lower())[0]
            )

        self.rows_added_count += 1
        return True
