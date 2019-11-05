from typing import Union

from django.db import models, connection
from django.core import checks
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from koocook_core.support.unit import *


__all__ = ['Quantity', 'QuantityField', 'parse_quantity']


class Quantity:
    __slots__ = ('amount', 'unit', 'nau')

    def __init__(self,
                 amount: float,
                 unit: Union[Unit, str],
                 nau: bool = False):
        self.nau = nau
        if isinstance(amount, float):
            self.amount = amount
        else:
            self.amount = float(amount)
        if nau:
            self.unit = type('NonUnit', (), {})
            if amount == 1:
                self.unit.singular = unit
            else:
                self.unit.plural = unit
            return
        self.unit = get_unit(unit)

    def __str__(self):
        if self.amount == 1:
            return '{:.0f} {}'.format(self.amount, self.unit.singular)
        if self.amount.is_integer():
            return '{:.0f} {}'.format(self.amount, self.unit.plural)
        return '{} {}'.format(self.amount, self.unit.plural)

    def get_db_str(self):
        return self.__str__() + ' /nau' if self.nau else ''

    @property
    def not_a_unit(self):
        return self.nau


def parse_quantity(quantity_string: str) -> Quantity:
    amount, *unit, nau = quantity_string.split(' ')
    if nau != '/nau':
        unit = unit + [nau]
        nau = False
    amount = float(amount)
    unit = ' '.join(unit)
    if nau:
        nau = True
    try:
        return Quantity(amount, unit, nau)
    except ValueError as e:
        raise ValidationError(_("Invalid input for a Quantity instance")
                              ) from e


class QuantityField(models.Field):
    description = _("<number><space><unit> (up to %(max_length)s)")

    def __init__(self, nau: bool = False, *args, **kwargs):
        self.nau = nau
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        # Only include kwarg if it's not the default
        if self.nau:
            kwargs['nau'] = self.nau
        return name, path, args, kwargs

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
            return value.get_db_str()

        if value is None:
            return value

        if isinstance(value, str):
            if ' /nau' in value:
                return value
            return value + ' /nau' if self.nau else ''
        return parse_quantity(value).get_db_str()

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
