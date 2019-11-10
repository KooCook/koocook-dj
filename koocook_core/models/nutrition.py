import json

from django.contrib.postgres import fields
from django.db import models

from koocook_core import fields as koocookfields

__all__ = ['MetaIngredient', 'RecipeIngredient']


class MetaIngredient(models.Model):
    name = models.CharField(max_length=255)
    nutrients = fields.JSONField()
    # ingredient_set from Ingredient's ForeignKey


class RecipeIngredient(models.Model):
    quantity = koocookfields.QuantityField(
        max_length=50,
    )
    meta = models.ForeignKey(
        'koocook_core.MetaIngredient',
        on_delete=models.PROTECT,
    )
    description = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    substitute_set = models.ManyToManyField('self', blank=True)
    recipe = models.ForeignKey(
        'koocook_core.Recipe',
        on_delete=models.CASCADE,
    )

    @property
    def nutrition(self):
        pass
        return
