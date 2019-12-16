import json
import logging

from django.contrib.postgres import fields
from django.db import models
from koocook_core.support.quantity import Quantity, parse_quantity

import operator
from koocook_core import fields as koocookfields

__all__ = ['MetaIngredient', 'RecipeIngredient']

logger = logging.getLogger(__name__)


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

    def load_nutrient(self):
        try:
            from koocook_core.support.scripts import get_nutrients
        except ModuleNotFoundError:
            from koocook_core.management.commands._add_path import add_datatrans
            add_datatrans()
            from koocook_core.support.scripts import get_nutrients
        try:
            self.nutrient = get_nutrients(self.name)[0]
        except Exception as e:
            logger.exception(e)


class RecipeIngredient(models.Model):
    exclude = ('recipe', )
    quantity = koocookfields.QuantityField()
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
        # try:
        nutrients = self.meta.nutrient
        if not nutrients:
            try:
                self.meta.load_nutrient()
                self.meta.save()
                nutrients = self.meta.nutrient
            except Exception as e:
                logger.exception(e)
        # except KeyError:
        #     # nutrients = self.meta.nutrient
        #     # if 'quantity' in nutrients:
        #     #     nutrients['quantity'] = parse_quantity(
        #     #         nutrients['quantity']).decimal
        #     # else:
        #     #     return nutrition_list
        #     # nutrition_list.append(nutrients)
        #     return nutrition_list
        for nutrient in nutrients:
            if nutrient['nutrient'] not in map(operator.itemgetter('nutrient'), nutrition_list):
                nutrient['quantity'] = parse_quantity(
                    nutrient['quantity']).mul_quantity(self.quantity).decimal
                nutrition_list.append(nutrient)
            else:
                nutrient['quantity'] = parse_quantity(
                    nutrient['quantity']).mul_quantity(self.quantity).decimal
                i = nutrition_list.index(next(filter(
                    lambda index: index.get(
                        'nutrient') == nutrient['nutrient'],
                    nutrition_list
                )))
                nutrition_list[i]['quantity'] = str(self.sum_nutrient(
                    nutrition_list[i]['quantity'], nutrient['quantity']
                ))
        return nutrition_list

    @staticmethod
    def sum_nutrient(first_nutrient: str, second_nutrient: str) -> Quantity:
        result = parse_quantity(first_nutrient) + \
            parse_quantity(second_nutrient)
        return result.decimal

    @property
    def words_quantity(self):
        return str(self.quantity.representation)

    @property
    def words_name(self):
        return " " + self.meta.name
