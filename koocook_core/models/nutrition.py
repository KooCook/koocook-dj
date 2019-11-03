import enum
import json

from django.contrib.postgres import fields
from django.db import models

from koocook_core import fields as koocookfields


@enum.unique
class Unit(enum.Enum):
    GRAM = 'g'
    KILOGRAM = 'kg'
    MILLIGRAM = 'mg'
    LITER = 'L'
    MILLILITER = 'mL'
    CUP = 'cup'
    TABLESPOON = 'tbsp'
    TEASPOON = 'tsp'
    PINCH = 'pinch'


class Quantity:
    def __init__(self, quantity: str):
        parts = quantity.split(' ')
        assert len(parts) == 2
        self.amount = parts[0]
        self.unit = parts[1]

    def __str__(self):
        return '{} {}'.format(self.amount, self.unit)


@enum.unique
class NutrientType(enum.Enum):
    CARBOHYDRATE = 'carbohydrates'
    ...


class MetaIngredient(models.Model):
    name = models.CharField(max_length=63)
    nutrient = fields.JSONField()
    # ingredient_set from Ingredient's ForeignKey


class Ingredient(models.Model):
    quantity = koocookfields.QuantityField(max_length=50)
    meta = models.ForeignKey(
        'koocook_core.MetaIngredient',
        on_delete=models.PROTECT,
    )
    substitute_set = models.ManyToManyField('self')
    recipe = models.ForeignKey(
        'koocook_core.Recipe',
        on_delete=models.CASCADE,
    )

    @property
    def nutrition(self):
        pass
        return
