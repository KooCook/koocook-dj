from django.contrib.postgres import fields
from django.db import models

from koocook_core import fields as koocookfields

__all__ = ['Recipe', '']


def _default_image():
    return ('{"https://example.com/photos/1x1/photo.jpg",'
            ' "https: //example.com/photos/4x3/photo.jpg",'
            ' "https://example.com/photos/16x9/photo.jpg"}')


def _default_recipe_instructions():
    return '{""}'


class Recipe(models.Model):
    name = models.CharField(max_length=63)
    image = fields.ArrayField(models.URLField(), default=_default_image)
    video = models.URLField(null=True, blank=True)
    author = models.ForeignKey(
        'koocook_core.Author',
        on_delete=models.PROTECT,
    )
    date_published = models.DateTimeField()
    description = models.CharField(max_length=255)
    prep_time = models.DurationField(null=True, blank=True)
    cook_time = models.DurationField()
    # ingredient_set from Ingredient's ForeignKey
    recipe_instructions = fields.ArrayField(models.TextField(), default=_default_recipe_instructions)
    recipe_yield = koocookfields.QuantityField(max_length=50, nau=True)
    tag_set = models.ManyToManyField('koocook_core.Tag', blank=True)
    # comment_set from Comment's ForeignKey
    aggregate_rating = models.OneToOneField(
        'koocook_core.AggregateRating',
        on_delete=models.PROTECT,
    )

    @property
    def total_time(self):
        return self.prep_time + self.cook_time

    @property
    def nutrition(self):
        pass
        return

    @property
    def recipe_ingredient(self):
        """ Proxy property for consistency with Schema.org's standard """
        return self.ingredient_set
