from typing import Union, Optional

import enum

__all__ = ['Unit', 'LengthUnit', 'AreaUnit', 'VolumeUnit', 'MassUnit',
           'TemperatureUnit']


@enum.unique
class Unit(enum.Enum):
    def __new__(cls, symbol: Optional[str], *args):
        obj = object.__new__(cls)
        # ``symbol`` is canonical value
        obj._value_ = symbol
        return obj

    def __init__(self, symbol: Optional[str], conversion_factor: Optional[float], *args):
        cls = self.__class__
        self._conversion_factor = conversion_factor
        if len(args) > 1 and args[1] is not None:
            self._singular = args[1]
        else:
            self._singular = ' '.join(self._name_.lower().split('_'))
        if len(args) > 0 and args[0] is not None:
            self._plural = args[0]
        else:
            self._plural = self._singular + 's'
        for other_value in (self._singular, self._plural, *args[2:]):
            cls._value2member_map_[other_value] = self

    @property
    def symbol(self) -> Optional[str]:
        return self._value_

    @property
    def singular(self) -> str:
        return self._singular

    @property
    def plural(self) -> str:
        return self._plural

    @property
    def conversion_factor(self) -> float:
        if self._conversion_factor is not None:
            return self._conversion_factor
        raise AttributeError('\'{}\' are incompatible with conversion factor'
                             .format(self.__class__.__name__))


class LengthUnit(Unit):
    METRE = 'm', 1., None, None, 'meter', 'meters'
    CENTIMETRE = 'cm', 0.01, None, None, 'centimeter', 'centimeters'
    MILLIMETRE = 'mm', 0.001, None, None, 'millimeter', 'millimeters'
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

    def __init__(self, symbol: str, *args):
        if symbol[0] == '°':
            _singular = 'degree ' + self._name_.title()
            _plural = 'degrees ' + self._name_.title()
            args = (_plural, _singular, symbol[1:])
        else:
            _singular = self._name_.lower()
            _plural = self._name_.lower() + 's'
            args = (_plural, _singular)
        super().__init__(symbol, None, *args)

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
