import enum
from typing import Union, Optional, Iterable, Type
from koocook_core.support.fraction import Fraction

__all__ = ['Unit', 'units', 'LengthUnit', 'AreaUnit', 'VolumeUnit', 'MassUnit',
           'TemperatureUnit', 'SpecialUnit', 'get_unit']


@enum.unique
class Unit(enum.Enum):

    # IDENTIFIER = (symbol or None, conversion factor or None[, plural form][, singular form][, synonyms ...])

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
        if self._singular:
            return self._singular
        return ''

    @property
    def plural(self) -> str:
        if self._plural:
            return self._plural
        return ''

    @property
    def representation(self):
        return self.get_repr()

    def get_repr(self):
        if self.singular:
            return self.singular
        else:
            return self.symbol

    @property
    def type(self) -> str:
        name = self.__class__.__name__
        return name[0].lower() + name[1:]

    @property
    def conversion_factor(self) -> float:
        if self._conversion_factor is not None:
            return self._conversion_factor
        raise AttributeError('\'{}\' are incompatible with conversion factor'
                             .format(self.__class__.__name__))

    def as_dict(self):
        try:
            return {"unit": self.get_repr(),
                    "singular": self.singular,
                    "plural": self.plural,
                    "symbol": self.symbol,
                    "value": self.conversion_factor}
        except AttributeError:
            if self.symbol:
                return {"symbol": self.symbol, "unit": self.get_repr(), "value": "REQ_FUNC"}
            else:
                return {"symbol": self.singular, "unit": self.get_repr(), "value": None}


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
    MICROGRAM = '\u03bcg', 0.000_000_001, None, None, '\u00b5g'

    OUNCE = 'oz', 0.028  # US Food nutrition labeling
    POUND = 'lb', 0.453592  # Google


class EnergyUnit(Unit):
    JOULE = 'J', 1.
    KILOJOULE = 'kJ', 1000.
    KILOCALORIE = 'kcal', 4184.
    CALORIE = 'cal', 4.184
    FOOD_CALORIE = 'Cal', 4184., 'Calories', 'Calorie'


class TemperatureUnit(Unit):
    CELSIUS = '°C',
    FAHRENHEIT = '°F',
    KELVIN = 'K',
    RANKINE = '°R',

    def __init__(self, symbol: str, *args):
        if symbol[0] == '°':
            _singular = 'degree ' + self._name_.title()
            _plural = 'degrees ' + self._name_.title()
            args = (_plural, _singular, symbol[1:], self._name_.title())
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


class SpecialUnit(Unit):
    NONE = 'None', None, 'units', 'unit'
    IU = 'IU', None, 'International Units', 'International Unit'
    SERVING = None, None,
    PERSON = None, None, 'people'

    def as_dict(self):
        if self is SpecialUnit.NONE:
            return {"unit": self.get_repr(),
                    "symbol": '',
                    "value": None}
        else:
            return super().as_dict()


def get_unit(unit: Union[str, Unit]) -> Unit:
    """Get Unit of Error from string

    Raises:
        ValueError: When `unit` is not a valid ``Unit``
    """
    if isinstance(unit, Unit):
        return unit
    else:
        for _unit_ in units:
            try:
                return _unit_(unit)
            except ValueError:
                pass
        else:
            raise ValueError('\'{}\' is not a valid Unit'.format(unit))


def convert(value: Union[int, float, Fraction],
            base_unit: Union[LengthUnit, VolumeUnit, MassUnit, EnergyUnit, Unit, str],
            quote_unit: Union[LengthUnit, VolumeUnit, MassUnit, EnergyUnit, Unit, str]
            ) -> Union[float, Fraction]:
    """Return converted value.

    Args:
        value (int, float, Fraction): value that need to convert.
        base_unit (LengthUnit, VolumeUnit, MassUnit, EnergyUnit, Unit, str): current unit.
        quote_unit (LengthUnit, VolumeUnit, MassUnit, EnergyUnit, Unit, str): unit that need to convert to.
    """
    factor = get_unit(base_unit).conversion_factor / get_unit(quote_unit).conversion_factor
    return value * factor


units: Iterable[Type[Unit]] = (LengthUnit, AreaUnit, VolumeUnit, MassUnit, TemperatureUnit, EnergyUnit, SpecialUnit)
