from django.core.validators import MinValueValidator
from django.contrib.postgres.fields import ArrayField
from django.db import models

from .nutrition import NutritionInfo, Ingredient
from .user import RecipeAuthor
from .tag import Tag


class Recipe(models.Model):
    name = models.CharField(max_length=100)
    image = models.URLField()
    author = models.ForeignKey(RecipeAuthor, on_delete=models.PROTECT)
    date_published = models.DateTimeField()
    description = models.CharField(max_length=255)
    prep_time = models.DurationField()
    cook_time = models.DurationField()

    @property
    def total_time(self):
        return self.prep_time + self.cook_time

    tags = models.ManyToManyField(Tag)

    recipe_yield = models.CharField(max_length=100)
    recipe_category = models.CharField(max_length=100)
    recipe_cuisine = models.CharField(max_length=100)

    nutrition_info = models.OneToOneField(NutritionInfo, on_delete=models.CASCADE)
    # use another object to preserve intuitiveness

    recipe_ingredient = models.ManyToManyField(Ingredient)
    recipe_instructions = ArrayField(models.TextField())

    @property
    def aggregate_rating(self):
        return
