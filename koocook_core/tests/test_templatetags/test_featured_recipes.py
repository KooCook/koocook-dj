import datetime
from django.urls import reverse
from django.test import TestCase
from django.utils import timezone
from koocook_core.models.recipe import Recipe
from koocook_core.models.review import AggregateRating
from koocook_core.templatetags.recipe_extras import top_latest_recipes


class FeaturedRecipesTests(TestCase):
    # TODO fix django.db.utils.ProgrammingError: type "hstore" does not exist
    def test_top_latest_with_different_date(self):
        create_recipe(recipe_name='1st recipe')
        create_recipe(recipe_name='2st recipe')
        self.assertQuerysetEqual(
            top_latest_recipes(Recipe.objects.all()),
            ['<Recipe: Recipe object (2)>', '<Recipe: Recipe object (1)>']
        )

    def test_top_latest_with_same_date(self):
        rating1 = create_aggregate_rating(rating=2)
        create_recipe(recipe_name='1st recipe', days=-1, rating=rating1)
        rating2 = create_aggregate_rating(rating=5)
        create_recipe(recipe_name='2st recipe', days=-1, rating=rating2)
        self.assertQuerysetEqual(
            top_latest_recipes(Recipe.objects.all()),
            ['<Recipe: Recipe object (2)>', '<Recipe: Recipe object (1)>']
        )


def create_aggregate_rating(rating):
    return AggregateRating.objects.create(rating_value=rating, rating_count=1)


def create_recipe(recipe_name, days=0, rating=AggregateRating.objects.create(rating_value=0, rating_count=1)):
    """ Create recipe model with given recipe_name, days, and rating"""
    time = timezone.now() + datetime.timedelta(days=days)
    return Recipe.objects.create(name=recipe_name, date_published=time,
                                 aggregate_rating=rating,
                                 recipe_instructions={})
