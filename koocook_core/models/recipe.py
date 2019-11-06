from django.contrib.postgres import fields
from django.db import models

from koocook_core import fields as koocookfields

__all__ = ['Recipe']


class Recipe(models.Model):
    name = models.CharField(max_length=63)
    image = fields.ArrayField(models.CharField(max_length=200), null=True)
    video = models.URLField(null=True, blank=True)
    author = models.ForeignKey(
        'koocook_core.Author',
        on_delete=models.PROTECT,
        null=True,
    )
    date_published = models.DateTimeField()
    # description = models.CharField(max_length=255)
    description = models.TextField()
    prep_time = models.DurationField(null=True, blank=True)
    cook_time = models.DurationField(null=True)
    # recipeingredient_set from Ingredient's ForeignKey
    recipe_instructions = fields.ArrayField(models.TextField())
    recipe_yield = koocookfields.QuantityField(max_length=50, nau=True, null=True)
    tag_set = models.ManyToManyField('koocook_core.Tag', blank=True)
    # comment_set from Comment's ForeignKey
    aggregate_rating = models.OneToOneField(
        'koocook_core.AggregateRating',
        on_delete=models.PROTECT, blank=True, null=True, default=None
    )

    @property
    def total_time(self):
        return self.prep_time + self.cook_time

    @property
    def nutrition(self):
        pass
        return
