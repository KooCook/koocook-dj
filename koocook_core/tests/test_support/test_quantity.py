import unittest

from koocook_core.support import quantity, unit


class TestQuantity(unittest.TestCase):
    int_amounts = tuple(range(20))
    float_amounts = tuple(x / 8 for x in range(20))
    amounts = int_amounts + float_amounts

    def setUp(self) -> None:
        self.quantity1 = quantity.parse_quantity('1/3 g')
        self.quantity2 = quantity.parse_quantity('2/3 g')
        self.quantity3 = quantity.parse_quantity('3 g')
        self.quantity4 = quantity.parse_quantity('1 g')
        self.quantity5 = quantity.parse_quantity('4 g')
        self.quantity6 = quantity.parse_quantity('4/3 g')

    def test_quantity_amount_can_be_int(self):
        for amount in TestQuantity.int_amounts:
            with self.subTest(amount=amount):
                try:
                    quantity.Quantity(amount, unit.MassUnit.GRAM)
                except ValueError as e:
                    raise self.failureException(f'test raised {e.__class__.__name__} unexpectedly') from e

    def test_quantity_amount_can_be_float(self):
        for amount in TestQuantity.float_amounts:
            with self.subTest(amount=amount):
                try:
                    quantity.Quantity(amount, unit.MassUnit.GRAM)
                except ValueError as e:
                    raise self.failureException(f'test raised {e.__class__.__name__} unexpectedly') from e

    def test_quantity_unit_can_be_Unit(self):
        for U in unit.units:
            for u in U:
                with self.subTest(unit=u):
                    try:
                        quantity.Quantity(1, u)
                        quantity.Quantity(2., u)
                    except ValueError as e:
                        raise self.failureException(f'test raised {e.__class__.__name__} unexpectedly') from e

    def test_quantity_unit_can_be_str_symbol(self):
        for U in unit.units:
            for u in U:
                with self.subTest(unit=u):
                    try:
                        quantity.Quantity(1, u.symbol)
                        quantity.Quantity(1.5, u.symbol)
                    except ValueError as e:
                        raise self.failureException(f'test raised {e.__class__.__name__} unexpectedly') from e

    def test_quantity_unit_can_be_str_plural(self):
        for U in unit.units:
            for u in U:
                with self.subTest(unit=u):
                    try:
                        quantity.Quantity(0.5, u.plural)
                        quantity.Quantity(1.5, u.plural)
                    except ValueError as e:
                        raise self.failureException(f'test raised {e.__class__.__name__} unexpectedly') from e

    def test_quantity_unit_can_be_str_singular(self):
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

    def test_add_with_both_amount_are_fraction(self):
        summation1 = self.quantity1 + self.quantity1
        with self.subTest():
            self.assertEqual(summation1, self.quantity2)
        summation2 = self.quantity1 + self.quantity2
        with self.subTest():
            self.assertEqual(summation2, self.quantity4)

    def test_add_with_both_amount_are_int(self):
        summation = self.quantity3 + self.quantity4
        self.assertEqual(summation, self.quantity5)

    def test_add_fraction_with_int(self):
        summation = self.quantity1 + self.quantity4
        self.assertEqual(summation, self.quantity6)

    def test_add_different_unit(self):
        summation = quantity.parse_quantity('0.002 kg') + self.quantity4
        self.assertEqual(summation, quantity.parse_quantity('0.003 kg'))

    def test_same_quantity_many_times(self):
        result = quantity.Quantity.mul_quantity(self.quantity1, self.quantity3)
        self.assertEqual(result, self.quantity4)

    def test_mul_same_unit(self):
        result = self.quantity1 * self.quantity3
        self.assertEqual(result, self.quantity4)

    def test_mul_different_unit(self):
        result = self.quantity4 * quantity.parse_quantity('3000 mg')
        self.assertEqual(result, self.quantity3)
