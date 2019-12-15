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
                 amount: Union[Fraction, int],
                 unit: Union[unit_.Unit, str]):
        if isinstance(amount, Fraction):
            self.amount = amount
        else:
            self.amount = Fraction(amount)
        self.unit = unit_.get_unit(unit)

    @property
    def decimal(self):
        if self.amount == 1:
            return '{} {}'.format(f"{float(self.amount)}", self.unit.singular)
        return '{} {}'.format(f"{float(self.amount)}", self.unit.plural)

    @property
    def representation(self):
        if self.amount == 1:
            return '{} {}'.format(f"$${self.as_latex()}$$", self.unit.singular)
        return '{} {}'.format(f"$${self.as_latex()}$$", self.unit.plural)

    def __str__(self):
        if self.amount == 1:
            return f'{self.amount} {self.unit.singular}'
        return f'{self.amount} {self.unit.plural}'

    def get_db_str(self):
        if self.unit.symbol:
            return f'{self.amount} {self.unit.symbol}'
        return self.__str__()

    # Monkey patched
    def __len__(self):
        return len(str(self))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return other.amount == self.amount and other.unit == self.unit

    def __add__(self, other):
        if self.unit == other.unit:
            result = self.amount + other.amount
        else:
            result = self.amount + unit_.convert(value=other.amount, base_unit=other.unit, quote_unit=self.unit)
        return Quantity(result, self.unit)

    def __mul__(self, other):
        if self.unit == other.unit:
            result = self.amount * other.amount
        else:
            result = self.amount * unit_.convert(value=other.amount, base_unit=other.unit, quote_unit=self.unit)
        return Quantity(result, self.unit)

    def __truediv__(self, other):
        if self.unit == other.unit:
            result = self.amount / other.amount
        else:
            result = self.amount / unit_.convert(value=other.amount, base_unit=other.unit, quote_unit=self.unit)
        return Quantity(result, self.unit)

    def as_latex(self):
        if self.amount.denominator > 1:
            return f'\\frac{{{self.amount.numerator}}}{{{self.amount.denominator}}}'
        else:
            return str(self.amount.numerator)

    def mul_quantity(self, quantity):
        amount = self.amount * quantity.amount
        return Quantity(amount, self.unit)


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
        self.max_length = 50
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs.pop('max_length')
        return name, path, args, kwargs

    def from_db_value(self, value, expression, connection):
        if value is None or value == '':
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
