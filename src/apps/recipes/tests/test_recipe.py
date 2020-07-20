import random

from django.test import TestCase
import faker

from apps.recipes.models import RecipeInstructions


fake = faker.Faker()
very_long_steps = fake.texts(nb_texts=random.randint(50, 150), max_nb_chars=2000)
fake_steps_set = [
    None,
    ['Mix everything together and put it in the oven for 30 minutes'],
    ['Go to store', 'Buy cake', '???', 'Profit'],
    [],
    very_long_steps,
]


class RecipeInstructionsTests(TestCase):
    def setUp(self):
        self.ri_set = [
            RecipeInstructions(),
            RecipeInstructions(steps=fake_steps_set[1]),
            RecipeInstructions(steps=fake_steps_set[2]),
            RecipeInstructions(steps=fake_steps_set[3]),
            RecipeInstructions(steps=fake_steps_set[4]),
        ]

    def test_str_shows_correct_amount_of_steps(self):
        for i, ri in enumerate(self.ri_set):
            nb_steps = len(fake_steps_set[i]) if fake_steps_set[i] else 0
            self.assertRegex(ri.__str__(),
                             rf'\b{nb_steps}\b')

    def test_empty_displayable_steps_when_no_steps(self):
        self.assertEqual(self.ri_set[0].displayable_steps, '')
        self.assertEqual(self.ri_set[3].displayable_steps, '')

    def test_displayable_steps_include_all_steps(self):
        for i, ri in enumerate(self.ri_set):
            for s in (fake_steps_set[i] if fake_steps_set[i] else []):
                self.assertIn(s, ri.displayable_steps)
