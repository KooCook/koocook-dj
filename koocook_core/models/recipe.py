from django.contrib.postgres import fields
from django.db import models

from koocook_core import fields as koocookfields
from .review import AggregateRating

__all__ = ['Recipe']


class Recipe(models.Model):
    """

    Attributes:
        recipeingredient_set (RelatedManager): from ForeignKey in ``Ingredient``
        comment_set (RelatedManager): from ForeignKey in ``Comment``

    References:
        https://developers.google.com/search/docs/data-types/recipe
        https://schema.org/Recipe
    """
    name = models.CharField(max_length=255)
    image = fields.ArrayField(
        models.CharField(max_length=200),
        null=True,
        blank=True,
    )
    video = models.URLField(null=True, blank=True)
    author = models.ForeignKey(
        'koocook_core.Author',
        on_delete=models.PROTECT,
        null=True,
    )
    # Refactor this to use custom save() later https://stackoverflow.com/questions/1737017/django-auto-now-and-auto-now-add
    date_published = models.DateTimeField(
        auto_now_add=True,
        null=True,
    )
    description = models.TextField()
    prep_time = models.DurationField(null=True)
    cook_time = models.DurationField(null=True)
    recipe_instructions = fields.ArrayField(models.TextField(), default=list)
    recipe_yield = koocookfields.QuantityField(null=True)
    tag_set = models.ManyToManyField('koocook_core.Tag', blank=True)
    aggregate_rating = models.OneToOneField(
        'koocook_core.AggregateRating',
        on_delete=models.PROTECT,
        blank=True,
        default=AggregateRating.create_empty,
    )

    @property
    def total_time(self):
        return self.prep_time + self.cook_time

    @property
    def nutrition(self):
        return

    @property
    def recipe_ingredients(self):
        """ Proxy property for consistency with Schema.org's standard """
        return self.recipeingredient_set.all()
