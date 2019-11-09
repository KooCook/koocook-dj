from __future__ import annotations

import math
import re
from typing import Tuple, Union, Match

VULGAR_UNICODE = {
    '¼': '1/4',
    '½': '1/2',
    '¾': '3/4',
    '⅐': '1/7',
    '⅑': '1/9',
    '⅓': '1/3',
    '⅔': '2/3',
    '⅕': '1/5',
    '⅖': '2/5',
    '⅗': '3/5',
    '⅘': '4/5',
    '⅙': '1/6',
    '⅛': '1/8',
    '⅜': '3/8',
    '⅝': '5/8',
    '⅞': '7/8',
    '⅟': '1/',
    '↉': '0/3',
}
VULGAR_UNICODE_PATTERN = re.compile(r'([0-9])?([{}])(-)?'.format(''.join(p for p in VULGAR_UNICODE)))
NUMERAL = {
    'one': 1,
    'two': 2,
    'three': 3,
    'four': 4,
    'five': 5,
    'six': 6,
    'seven': 7,
    'eight': 8,
    'nine': 9,
    'ten': 10,
    'eleven': 11,
    'twelve': 12,
}


def parse_numeral(s: str) -> str:
    """Converts numeral under 13 in string to number.

    Args:
        s (str): positional only. string to parse

    Examples:
        >>> parse_numeral('one to two cups parmesan')
        '1 to 2 cups parmesan'
        >>> parse_numeral('TEN BUCKS!')
        '10 BUCKS!'
        >>> parse_numeral('1234')
        '1234'
        >>> parse_numeral('something else ')
        'something else '
    """
    def repl(m: Match):
        return str(NUMERAL[m.group(0).lower()])
    pattern = re.compile('|'.join(k for k in NUMERAL), re.IGNORECASE)
    return pattern.sub(repl, s)


def parse_vulgar_unicode(s: str) -> str:
    """Converts string containing vulgar fractions in unicode to literal.

    Args:
        s (str): positional only. string to parse

    Examples:
        >>> parse_vulgar_unicode('¾ cup (1½ sticks) cold unsalted butter, cut into ¼-inch pieces')
        '3/4 cup (1 1/2 sticks) cold unsalted butter, cut into ¼-inch pieces'
        >>> parse_vulgar_unicode('1¼-inch strips')
        '1¼-inch strips'
        >>> parse_vulgar_unicode('1½')
        '1 1/2'
        >>> parse_vulgar_unicode('¾')
        '3/4'
        >>> parse_vulgar_unicode('¼')
        '1/4'
        >>> parse_vulgar_unicode('3⅟100')
        '3 1/100'
    """
    for k, v in VULGAR_UNICODE.items():
        x = s.find(k)
        a = ''
        if x != -1:
            if x > 0:
                if s[x - 1] in '0123456789':
                    a = ' '
            try:
                if s[x + 1] == '-':
                    continue
            except IndexError:
                pass
        s = s.replace(k, a + v)
    return s


def parse_fraction(s: str) -> Fraction:
    """Converts a fraction string to Fraction.

    Args:
        s (str): positional only. string to parse

    Examples:
        >>> parse_fraction('1/2') == Fraction(1, 2)
        True
        >>> parse_fraction('5/4') == Fraction(5, 4)
        True
        >>> parse_fraction('8/17.5') == Fraction(16, 35)
        True
        >>> parse_fraction('¼') == Fraction(1, 4)
        True
        >>> parse_fraction('⅟20') == Fraction(1, 20)
        True
        >>> parse_fraction('5') == Fraction(5)
        True
    """
    if '/' in s:
        try:
            numerator, denominator = map(float, s.split('/'))
            return Fraction(numerator, denominator)
        except ValueError:
            raise
    try:
        s = parse_vulgar_unicode(s)
        try:
            numerator, denominator = map(float, s.split('/'))
            return Fraction(numerator, denominator)
        except ValueError as e:
            try:
                numerator = float(s)
                return Fraction(numerator)
            except ValueError as ee:
                raise ee from e.__context__
    except ValueError:
        raise


def type_error_msg_1(self, operand: str, other) -> str:
    """Return a python built-in like error message"""
    return "unsupported operand type(s) for {0}: '{1}' and '{2}'".format(
        operand, self.__class__.__name__, other.__class__.__name__)


def type_error_msg_2(self, operand: str, other) -> str:
    """Return a python built-in like error message"""
    return "'{0}' not supported between instances of '{1}' and '{2}'".format(
        operand, self.__class__.__name__, other.__class__.__name__)


def to_proper(numerator: int, denominator: int) -> Tuple[int, int]:
    """Converts `numerator` and `denominator` to their simplest ratio.

    Examples:
        >>> to_proper(7, 28)
        (1, 4)
        >>> to_proper(-36, 54)
        (-2, 3)
        >>> to_proper(3, 4)
        (3, 4)
        >>> to_proper(0, 0)
        (0, 0)
    """
    if numerator == 0:
        if denominator == 0:
            return 0, 0
        return 0, 1
    if denominator == 0:
        if numerator > 0:
            return 1, 0
        return -1, 0
    gcd = math.gcd(numerator, denominator)
    assert gcd > 0
    assert (numerator / gcd).is_integer()
    assert (denominator / gcd).is_integer()
    sign = numerator * denominator / abs(numerator * denominator)
    return int(sign * abs(numerator) / gcd), int(abs(denominator) / gcd)


def to_ratio(x: Union[float, int]) -> Tuple[int, int]:
    """Converts number to a pair of integer ratio with positive denominator.

    Examples:
        >>> to_ratio(5.6)
        (28, 5)
        >>> to_ratio(0.875)
        (7, 8)
        >>> to_ratio(-0.048)
        (-6, 125)
        >>> to_ratio(math.inf)
        (1, 0)
        >>> to_ratio(math.nan)
        (0, 0)
        >>> to_ratio(1)
        (1, 1)
    """
    if math.isnan(x):
        return 0, 0
    if x == math.inf:
        return 1, 0
    if x == -math.inf:
        return -1, 0
    i = 0
    num = float(x)
    while not num.is_integer():
        num *= 10
        i += 1
    num = int(num)
    assert x == num / 10 ** i
    return to_proper(num, 10 ** i)


class Fraction:
    """A fraction with a numerator and denominator and arithmetic operations.

    Fractions are always stored in proper form, without common factors in
    numerator and denominator, and denominator >= 0.
    Since Fractions are stored in proper form, each value has a
    unique representation, e.g. 4/5, 24/30, and -20/-25 have the same
    internal representation.

    Attributes:
        numerator (int): the numerator of the fraction
        denominator (int): the denominator of the fraction
    """

    def __init__(self, numerator, denominator=1):
        """Initialize a new fraction with the given numerator
           and denominator (default 1).
        """
        if isinstance(numerator, int) and isinstance(denominator, int):
            self.numerator, self.denominator = to_proper(numerator, denominator)
        elif isinstance(numerator, float) or isinstance(denominator, float):
            frac = Fraction(*to_ratio(numerator)) / Fraction(*to_ratio(denominator))
            self.numerator, self.denominator = frac.numerator, frac.denominator
        else:
            raise TypeError("numerator must be 'int' or 'float'")
        assert isinstance(self.numerator, int)
        assert isinstance(self.denominator, int)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"{self.numerator}{f'/{self.denominator}' if self.denominator != 1 else ''}"

    def __float__(self):
        """Return the float representation of the fraction. 1/0 is considered as inf."""
        if self.is_infinite():
            sign = 1 if self.numerator > 0 else -1
            return sign * math.inf
        if self.isnan():
            return math.nan
        return self.numerator / self.denominator

    def __add__(self, other: Union[int, float, Fraction]) -> Union[Fraction, math.nan]:
        """Return the sum of two fractions as a new fraction.
           Use the standard formula  a/b + c/d = (ad+bc)/(b*d)
        """
        if not isinstance(other, Fraction):
            if not isinstance(other, (int, float)):
                raise TypeError(type_error_msg_1(self, '+', other))
            other = Fraction(other)

        if self.is_infinite() and other.is_infinite():
            if self.numerator > 0:
                if other.numerator > 0:
                    return Fraction(1, 0)
                # inf + -inf -> indefinite
                return Fraction(0, 0)
            if other.numerator < 0:
                return Fraction(-1, 0)
            # -inf + inf -> indefinite
            return Fraction(0, 0)
        return Fraction(self.numerator * other.denominator + other.numerator * self.denominator,
                        self.denominator * other.denominator)

    def __sub__(self, other: Union[int, float, Fraction]) -> Union[Fraction, math.nan]:
        if not isinstance(other, Fraction):
            if not isinstance(other, (int, float)):
                raise TypeError(type_error_msg_1(self, '-', other))
            other = Fraction(other)

        return self + (-other)

    def __mul__(self, other: Union[int, float, Fraction]) -> Union[Fraction, math.nan]:
        if not isinstance(other, Fraction):
            if not isinstance(other, (int, float)):
                raise TypeError(type_error_msg_1(self, '*', other))
            other = Fraction(other)

        return Fraction(self.numerator * other.numerator, self.denominator * other.denominator)

    def __truediv__(self, other: Union[int, float, Fraction]) -> Union[Fraction, math.nan]:
        if not isinstance(other, Fraction):
            if not isinstance(other, (int, float)):
                raise TypeError(type_error_msg_1(self, '/', other))
            other = Fraction(other)

        if self.denominator * other.numerator == 0:
            if self.numerator * other.denominator == 0:
                # zero over zero -> indefinite
                return Fraction(0, 0)
            if other.numerator < 0:
                # because negative zero = zero
                return Fraction(-self.numerator * other.denominator, 0)
        return Fraction(self.numerator * other.denominator, self.denominator * other.numerator)

    def __gt__(self, other: Fraction):
        if not isinstance(other, Fraction):
            if not isinstance(other, (int, float)):
                raise TypeError(type_error_msg_2(self, '>', other))
            other = Fraction(other)

        if self.isnan() or other.isnan():
            # nan cannot be ordered
            return False
        # avoids dividing because apparently multiplication is easier?
        return self.numerator * other.denominator > other.numerator * self.denominator

    def __lt__(self, other: Fraction):
        if not isinstance(other, Fraction):
            if not isinstance(other, (int, float)):
                raise TypeError(type_error_msg_2(self, '<', other))
            other = Fraction(other)

        if self.isnan() or other.isnan():
            # nan cannot be ordered
            return False
        # avoids dividing because apparently multiplication is easier?
        return self.numerator * other.denominator < other.numerator * self.denominator

    def __eq__(self, other):
        """Two fractions are equal if they have the same value.
           Fractions are stored in proper form so the internal representation
           is unique (3/6 is same as 1/2).
        """
        if isinstance(other, (int, float)):
            other = Fraction(other)
        else:
            if not isinstance(other, Fraction):
                return False
        # nan cannot be ordered
        if self.isnan() or other.isnan():
            return False
        return self.numerator == other.numerator and self.denominator == other.denominator

    def __neg__(self):
        return Fraction(-self.numerator, self.denominator)

    def is_infinite(self):
        """Returns True if limit of the fraction tends to infinity.

        Examples:
            >>> Fraction(1, 0).is_infinite()
            True
            >>> Fraction(0, 1).is_infinite()
            False
            >>> Fraction(-1, 0).is_infinite()
            True
        """
        return self.denominator == 0 and self.numerator in (1, -1)

    def isnan(self):
        """ Return True if fraction is a NaN (not a number), and False otherwise.

        Notes:
            named ``isnan`` to comply with the naming in the math module
        """
        return self.numerator == self.denominator == 0


if __name__ == '__main__':
    """Run the doctests in all methods."""
    import doctest

    doctest.testmod()
