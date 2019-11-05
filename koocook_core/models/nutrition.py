import enum
import json

from django.contrib.postgres import fields
from django.db import models

from koocook_core import fields as koocookfields

__all__ = ['MetaIngredient', 'Ingredient']


@enum.unique
class NutrientType(enum.Enum):
    CARBOHYDRATE = 'carbohydrates'
    ...


class MetaIngredient(models.Model):
    name = models.CharField(max_length=63)
    nutrient = fields.JSONField(default=dict)
    # ingredient_set from Ingredient's ForeignKey


class Ingredient(models.Model):
    quantity = koocookfields.QuantityField(max_length=50)
    meta = models.ForeignKey(
        'koocook_core.MetaIngredient',
        on_delete=models.PROTECT,
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
