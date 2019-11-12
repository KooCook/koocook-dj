import django.test as djangotest
import unittest

from koocook_core.support import quantity, unit


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
        'μg',
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
