import enum
import json

from django.contrib.postgres import fields
from django.db import models
from koocook_core.support.quantity import Quantity, parse_quantity

from koocook_core import fields as koocookfields

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
        return {'id': self.id, 'name': self.meta.name, 'type': self.quantity. unit.type,
                'quantity': {'unit': self.quantity.unit.symbol, 'number': self.quantity.amount}}

    @property
    def to_json(self):
        return json.dumps(self.to_dict)

    @property
    def nutrition(self):
        nutrition_list = []
        for nutrient in self.meta.nutrient:
            if nutrient['nutrient'] not in list(map(lambda x: x['nutrient'], nutrition_list)):
                nutrition_list.append(nutrient)
            else:
                for i in range(len(nutrition_list)):
                    if nutrition_list[i]['nutrient'] == nutrient['nutrient']:
                        nutrition_list[i]['quantity'] = str(RecipeIngredient.sum_nutrient(
                            nutrition_list[i]['quantity'], nutrient['quantity']
                        ))
        return nutrition_list

    @staticmethod
    def sum_nutrient(first_nutrient: str, second_nutrient: str):
        result = parse_quantity(first_nutrient) + parse_quantity(second_nutrient)
        return result
