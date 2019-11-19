from datetime import timedelta
from django.test import TestCase
from koocook_core.models.recipe import Recipe


class RecipeModelTests(TestCase):

    def test_total_time_with_prep_cook_time_are_second(self):
        time = timedelta(seconds=30)
        recipe = Recipe(prep_time=time, cook_time=time)
        self.assertEqual(recipe.total_time, timedelta(minutes=1))

    def test_total_time_with_prep_time_cook_time(self):
        time = timedelta(seconds=30)
        recipe = Recipe(prep_time=time, cook_time=time)
        self.assertEqual(recipe.total_time, timedelta(minutes=1))

    def test_total_time_with_zero_prep_time(self):
        recipe = Recipe(prep_time=timedelta(seconds=90), cook_time=timedelta(seconds=0))
        self.assertEqual(recipe.total_time, timedelta(minutes=1, seconds=30))

    def test_recipe_ingredient(self):
        recipe = Recipe()
        self.assertEqual(recipe.recipe_ingredient, recipe.ingredient_set)
