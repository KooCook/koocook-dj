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

    def save(self, *args, **kwargs):
        if self.nutrient:
            pass
        else:
            try:
                from koocook_core.support.scripts import get_nutrients
            except ModuleNotFoundError:
                from koocook_core.management.commands._add_path import add_datatrans
                add_datatrans()
                from koocook_core.support.scripts import get_nutrients
            self.nutrient = get_nutrients(self.name)
        super().save(*args, **kwargs)


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
        return
