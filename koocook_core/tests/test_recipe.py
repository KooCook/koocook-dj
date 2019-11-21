from datetime import timedelta
from django.test import TestCase
from koocook_core.models.recipe import Recipe


class RecipeModelTests(TestCase):
    def test_total_time_with_prep_cook_time_are_second(self):
        time = timedelta(seconds=30)
        recipe = Recipe(prep_time=time, cook_time=time)
        self.assertEqual(recipe.total_time, timedelta(minutes=1))
