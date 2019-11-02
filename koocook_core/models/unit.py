from typing import Union

import enum

__all__ = ['Unit', 'LengthUnit', 'AreaUnit', 'VolumeUnit', 'MassUnit',
           'TemperatureUnit']


@enum.unique
class Unit(enum.Enum):

    @property
    def symbol(self):
        return self._value_[0]

    @property
    def singular(self):
        if len(self._value_) > 3:
            return self._value_[3]
        return ' '.join(self._name_.lower().split('_'))

    @property
    def plural(self):
        if len(self._value_) > 2:
            return self._value_[2]
        return self.singular + 's'

    @property
    def conversion_factor(self) -> float:
        return self._value_[1]


class LengthUnit(Unit):
    METRE = 'm', 1.
    CENTIMETRE = 'cm', 0.01
    INCH = 'in', 0.0254, 'inches'


class AreaUnit(Unit):
    pass


class VolumeUnit(Unit):
    CUBIC_METRE = 'm<sup>3</sup>', 1.

    LITRE = 'L', 0.001
    MILLILITRE = 'mL', 0.000_001

    CUP = None, 0.000_240
    TABLESPOON = 'tbsp', 0.000_015
    TEASPOON = 'tsp', 0.000_005


class MassUnit(Unit):
    KILOGRAM = 'kg', 1.
    GRAM = 'g', 0.001
    MILLIGRAM = 'mg', 0.000_001


class TemperatureUnit(Unit):
    CELSIUS = '°C',
    FAHRENHEIT = '°F',
    KELVIN = 'K',
    RANKINE = '°R',

    @property
    def singular(self):
        if self is not TemperatureUnit.KELVIN:
            return 'degree ' + self._name_.title()
        return self._name_.lower()

    @property
    def plural(self):
        if self is not TemperatureUnit.KELVIN:
            return 'degrees ' + self._name_.title()
        return self._name_.lower() + 's'

    @staticmethod
    def convert(value: float,
                base_unit: Union['TemperatureUnit', str],
                quote_unit: Union['TemperatureUnit', str]) -> float:
        base_unit, quote_unit = map(TemperatureUnit, (base_unit, quote_unit))
        return _from_celsius(_to_celsius(value, base_unit), quote_unit)

    @property
    def conversion_factor(self) -> float:
        raise AttributeError('Temperature are in scales and are incompatible '
                             'with conversion factor')


def _to_celsius(value: float, base: Union[TemperatureUnit, str]) -> float:
    if base is TemperatureUnit.CELSIUS:
        return value
    if base is TemperatureUnit.KELVIN:
        return value - 273.15
    if base is TemperatureUnit.FAHRENHEIT:
        return (value - 32) * 5 / 9
    if base is TemperatureUnit.RANKINE:
        return (value - 491.67) * 5 / 9
    raise TypeError('invalid base \'{}\''.format(base.__class__.__name__))


def _from_celsius(value: float, quote: Union[TemperatureUnit, str]) -> float:
    if quote is TemperatureUnit.CELSIUS:
        return value
    if quote is TemperatureUnit.KELVIN:
        return value + 273.15
    if quote is TemperatureUnit.FAHRENHEIT:
        return value * 9 / 5 + 32
    if quote is TemperatureUnit.RANKINE:
        return (value + 273.15) * 9 / 5
    raise TypeError('invalid quote \'{}\''.format(quote.__class__.__name__))
