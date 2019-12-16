import unittest

from koocook_core.support import unit


class TestUnit(unittest.TestCase):
    units = (
        # Length
        'inches',
        # Area
        # Volume
        'tbsp',
        'cups',
        # Mass
        'ounces',
        'g',
        'mg',
        '\u03bcg',
        # Energy
        'J',
        'kJ',
        'Cal',
        'kcal',
        # Temperature
        'Celsius',
        'Fahrenheit',
        'C',
        'F',
        '°F',
        '°F',
        # Special
        'servings',
        'people',
        # None
        'unit',
    )

    non_units = (
        'asdfkasg',
        'eggs',
        'legs',
    )

    def test_get_unit(self):
        for u in TestUnit.units:
            with self.subTest(unit=u):
                try:
                    unit.get_unit(u)
                except ValueError as e:
                    raise self.failureException(f'test raised {e.__class__.__name__} unexpectedly') from e

    def test_get_unit_raises_ValueError(self):
        for u in TestUnit.non_units:
            with self.subTest(unit=u):
                with self.assertRaises(ValueError):
                    unit.get_unit(u)

    def test_convert_unit_from_small_to_big(self):
        """ convert g to kg"""
        result = unit.convert(1, 'g', 'kg')
        self.assertEqual(result, 0.001)

    def test_convert_unit_from_big_to_small(self):
        """ convert kg to g"""
        result = unit.convert(1, 'kg', 'g')
        self.assertEqual(result, 1000.)

    def test_convert_temperature(self):
        """ convert °F to K"""
        result = f"{unit.TemperatureUnit.convert(0, '°F', 'K'):.3f}"
        self.assertEqual(result, '255.372')
