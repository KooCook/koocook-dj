import enum
import json

from django.contrib.postgres import fields
from django.db import models
from koocook_core.support.quantity import Quantity, parse_quantity

from koocook_core import fields as koocookfields

from typing import List

__all__ = ['MetaIngredient', 'RecipeIngredient']


@enum.unique
class NutrientType(enum.Enum):
    CARBOHYDRATE = 'carbohydrates'
    ...


class MetaIngredient(models.Model):
    """
        Note: ingredient_set from Ingredient's ForeignKey
    """
    name = models.CharField(max_length=255)
    # Monkey patched
    nutrient = fields.JSONField(default=dict)
    description = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )


class RecipeIngredient(models.Model):
    quantity = koocookfields.QuantityField(
        max_length=50,
    )
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
    def to_dict(self):
        return {'id': self.id, 'name': self.meta.name, 'type': self.quantity.unit.type,
                'quantity': {'unit': self.quantity.unit.symbol, 'number': self.quantity.amount,
                             'rendered': self.quantity.as_latex()},
                'repr': f"{self.quantity.representation} of {self.meta.name}"}

    @property
    def to_json(self):
        return json.dumps(self.to_dict)

    @property
    def nutrition(self):
        nutrition_list = []
        try:
            nutrients = self.meta.nutrient[0]
        except KeyError:
            nutrients = self.meta.nutrient
            return nutrition_list
        for nutrient in nutrients:
            if nutrient['nutrient'] not in list(map(lambda x: x['nutrient'], nutrition_list)):
                nutrient['quantity'] = parse_quantity(nutrient['quantity']).mul_quantity(self.quantity)
                nutrition_list.append(nutrient)
            else:
                nutrient['quantity'] = parse_quantity(nutrient['quantity']).mul_quantity(self.quantity)
                i = nutrition_list.index(next(filter(
                    lambda index: index.get('nutrient') == nutrient['nutrient'],
                    nutrition_list
                )))
                nutrition_list[i]['quantity'] = str(RecipeIngredient.sum_nutrient(
                    nutrition_list[i]['quantity'], nutrient['quantity']
                ))
        return nutrition_list

    @staticmethod
    def sum_nutrient(first_nutrient: str, second_nutrient: str) -> Quantity:
        result = parse_quantity(first_nutrient) + parse_quantity(second_nutrient)
        return result
