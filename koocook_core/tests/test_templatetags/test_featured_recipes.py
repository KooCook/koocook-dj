import datetime
from django.urls import reverse
from django.test import TestCase
from django.utils import timezone
from koocook_core.models.recipe import Recipe
from koocook_core.models.review import AggregateRating
from koocook_core.templatetags.recipe_extras import top_latest_recipes


class FeaturedRecipesTest(TestCase):
    def test_top_latest_with_different_date(self):
        rating1 = create_aggregate_rating(rating=2)
        rating2 = create_aggregate_rating(rating=2)
        create_recipe(recipe_name='1st recipe', days=-5, rating=rating1)
        create_recipe(recipe_name='2st recipe', days=-2, rating=rating2)
        self.assertQuerysetEqual(
            top_latest_recipes(Recipe.objects.all()),
            ['<Recipe: Recipe object (2)>', '<Recipe: Recipe object (1)>']
        )

    def test_top_latest_with_same_date(self):
        rating1 = create_aggregate_rating(rating=2)
        rating2 = create_aggregate_rating(rating=5)
        create_recipe(recipe_name='1st recipe', days=-1, rating=rating2)
        create_recipe(recipe_name='2st recipe', days=-1, rating=rating1)
        self.assertQuerysetEqual(
            top_latest_recipes(Recipe.objects.all()),
            ['<Recipe: Recipe object (3)>', '<Recipe: Recipe object (4)>']
        )

    def test_empty_recipe(self):
        self.assertQuerysetEqual(
            top_latest_recipes(Recipe.objects.all()), []
        )


def create_aggregate_rating(rating):
    return AggregateRating.objects.create(rating_value=rating, rating_count=1)


def create_recipe(recipe_name, days=0, rating=AggregateRating.objects.create(rating_value=1, rating_count=1)):
    """ Create recipe model with given recipe_name, days, and rating"""
    time = timezone.now() + datetime.timedelta(days=days)
    time.strftime('%d.%m.%Y %H:%M:%S')
    return Recipe.objects.create(name=recipe_name, date_published=time,
                                 recipe_instructions=[], aggregate_rating=rating)
