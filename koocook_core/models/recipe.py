from django.contrib.postgres import fields
from django.db import models

from koocook_core import fields as koocookfields


class Recipe(models.Model):
    name = models.CharField(max_length=63)
    image = fields.ArrayField(models.URLField())
    author = models.ForeignKey(
        'koocook_core.Author',
        on_delete=models.PROTECT,
    )
    date_published = models.DateTimeField()
    description = models.CharField(max_length=255)
    prep_time = models.DurationField(null=True, blank=True)
    cook_time = models.DurationField()
    # ingredient_set from Ingredient's ForeignKey
    recipe_instructions = fields.ArrayField(models.TextField())
    tag_set = models.ManyToManyField('koocook_core.Tag')
    recipe_yield = koocookfields.QuantityField(max_length=50)
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
