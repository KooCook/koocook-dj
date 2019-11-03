from typing import Union

from django.db import models, connection
from django.core import checks
from django.utils.translation import gettext_lazy as _

from koocook_core.support.unit import *


__all__ = ['Quantity', 'QuantityField']


class Quantity:
    __slots__ = ('amount', 'unit')

    def __init__(self, amount: float, unit: Union[Unit, str]):
        if isinstance(amount, float):
            self.amount = amount
        else:
            self.amount = float(amount)
        if isinstance(unit, Unit):
            self.unit = unit
        else:
            for _unit_ in Units:
                try:
                    self.unit = _unit_(unit)
                    break
                except ValueError:
                    pass
            else:
                raise ValueError('\'{}\' is not a valid Unit'.format(unit))

    def __str__(self):
        return '{} {}'.format(self.amount, self.unit)


def parse_quantity(quantity_string: str) -> Quantity:
    amount, *unit = quantity_string.split(' ')
    amount = float(amount)
    unit = ' '.join(unit)
    try:
        return Quantity(amount, unit)
    except ValueError as e:
        raise ValueError(_("Invalid input for a Quantity instance"))


class QuantityField(models.Field):
    description = _("<number><space><unit> (up to %(max_length)s)")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def check(self, **kwargs):
        return [
            *super().check(**kwargs),
            *self._check_max_length_attribute(**kwargs),
        ]

    def _check_max_length_attribute(self, **kwargs):
        if self.max_length is None:
            return [
                checks.Error(
                    "CharFields must define a 'max_length' attribute.",
                    obj=self,
                    id='fields.E120',
                )
            ]
        elif (not isinstance(self.max_length, int) or isinstance(self.max_length, bool) or
                self.max_length <= 0):
            return [
                checks.Error(
                    "'max_length' must be a positive integer.",
                    obj=self,
                    id='fields.E121',
                )
            ]
        else:
            return []

    def cast_db_type(self, connection):
        if self.max_length is None:
            return connection.ops.cast_char_field_without_max_length
        return super().cast_db_type(connection)

    def get_internal_type(self):
        return 'CharField'

    def from_db_value(self, value, expression, connection):
        if value is None:
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
            return str(value)

        if value is None:
            return value

        if isinstance(value, str):
            return value
        return str(parse_quantity(value))

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return self.get_prep_value(value)

    def formfield(self, **kwargs):
        # Passing max_length to forms.CharField means that the value's length
        # will be validated twice. This is considered acceptable since we want
        # the value in the form field (to pass into widget for example).
        defaults = {'max_length': self.max_length}
        # TODO: Handle multiple backends with different feature flags.
        if self.null and not connection.features.interprets_empty_strings_as_nulls:
            defaults['empty_value'] = None
        defaults.update(kwargs)
        return super().formfield(**defaults)
