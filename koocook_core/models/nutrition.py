import json

from django.contrib.postgres import fields
from django.db import models

from koocook_core import fields as koocookfields

__all__ = ['MetaIngredient', 'RecipeIngredient']


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
        null=True,  # monkey patch
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
        return
