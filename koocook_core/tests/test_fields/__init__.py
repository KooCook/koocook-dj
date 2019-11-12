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


class TestQuantity(unittest.TestCase):
    int_amounts = (
        0,
        1,
        2,
        3,
        9,
    )

    float_amounts = (
        0.5,
        1.,
        1.5,
    )

    amounts = int_amounts + float_amounts

    def test_amount_can_be_int(self):
        for amount in TestQuantity.int_amounts:
            with self.subTest(amount=amount):
                try:
                    quantity.Quantity(amount, unit.MassUnit.GRAM)
                except ValueError as e:
                    raise self.failureException(f'test raised {e.__class__.__name__} unexpectedly') from e

    def test_amount_can_be_float(self):
        for amount in TestQuantity.float_amounts:
            with self.subTest(amount=amount):
                try:
                    quantity.Quantity(amount, unit.MassUnit.GRAM)
                except ValueError as e:
                    raise self.failureException(f'test raised {e.__class__.__name__} unexpectedly') from e

    def test_unit_can_be_Unit(self):
        for U in unit.units:
            for u in U:
                with self.subTest(unit=u):
                    try:
                        quantity.Quantity(1, u)
                        quantity.Quantity(2., u)
                    except ValueError as e:
                        raise self.failureException(f'test raised {e.__class__.__name__} unexpectedly') from e

    def test_unit_can_be_str_symbol(self):
        for U in unit.units:
            for u in U:
                with self.subTest(unit=u):
                    try:
                        quantity.Quantity(1, u.symbol)
                        quantity.Quantity(1.5, u.symbol)
                    except ValueError as e:
                        raise self.failureException(f'test raised {e.__class__.__name__} unexpectedly') from e

    def test_unit_can_be_str_plural(self):
        for U in unit.units:
            for u in U:
                with self.subTest(unit=u):
                    try:
                        quantity.Quantity(0.5, u.plural)
                        quantity.Quantity(1.5, u.plural)
                    except ValueError as e:
                        raise self.failureException(f'test raised {e.__class__.__name__} unexpectedly') from e

    def test_unit_can_be_str_singular(self):
        for U in unit.units:
            for u in U:
                with self.subTest(unit=u):
                    try:
                        quantity.Quantity(1, u.singular)
                        quantity.Quantity(1., u.singular)
                    except ValueError as e:
                        raise self.failureException(f'test raised {e.__class__.__name__} unexpectedly') from e

    def test_parse_quantity_is_inverse_of_get_db_str(self):
        for U in unit.units:
            for u in U:
                for amount in TestQuantity.amounts:
                    with self.subTest(amount=amount, unit=u):
                        try:
                            quantity.parse_quantity(quantity.Quantity(amount, u).get_db_str())
                        except ValueError as e:
                            raise self.failureException(f'test raised {e.__class__.__name__} unexpectedly') from e
