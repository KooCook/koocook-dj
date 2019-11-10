from typing import Union

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from koocook_core.support import unit as unit_
from koocook_core.support.fraction import Fraction

__all__ = ['Quantity', 'QuantityField', 'parse_quantity']


class Quantity:
    __slots__ = ('amount', 'unit')

    def __init__(self,
                 amount: Fraction,
                 unit: Union[unit_.Unit, str]):
        if isinstance(amount, Fraction):
            self.amount = amount
        else:
            self.amount = Fraction(amount)
        self.unit = unit_.get_unit(unit)

    def __str__(self):
        if self.amount == 1:
            return '{} {}'.format(self.amount, self.unit.singular)
        return '{} {}'.format(self.amount, self.unit.plural)

    def get_db_str(self):
        return '{} {}'.format(self.amount, self.unit.symbol)

    @property
    def not_a_unit(self):
        return self.unit is unit_.SpecialUnit.NONE


def parse_quantity(quantity_string: str) -> Quantity:
    amount, *unit = quantity_string.split(' ')
    amount = Fraction(amount)
    try:
        return Quantity(amount, ' '.join(unit))
    except ValueError as e:
        raise ValidationError(_("Invalid input for a Quantity instance")
                              ) from e


class QuantityField(models.CharField):
    description = _("<number><space><unit> (up to %(max_length)s)")

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 50
        super().__init__(*args, **kwargs)

    # def deconstruct(self):
    #     name, path, args, kwargs = super().deconstruct()
    #     # Only include kwarg if it's not the default
    #     if self.nau:
    #         kwargs['nau'] = self.nau
    #     return name, path, args, kwargs

    def from_db_value(self, value, expression, connection):
        if value is None or value is '':
            return value
        return parse_quantity(value)

    def to_python(self, value):
        if isinstance(value, Quantity):
            return value

        if value is None:
            return value

        return parse_quantity(value)

    def get_prep_value(self, value):
        if isinstance(value, Quantity):
            return value.get_db_str()

        if value is None:
            return value

        return parse_quantity(value).get_db_str()

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return self.get_prep_value(value)
