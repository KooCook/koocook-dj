import math
import re
from typing import Tuple, Union, Match, cast

__all__ = ['NUMBER_PATTERN', 'Fraction', 'parse_str', 'parse_match',
           'parse_fraction', 'parse_vulgar_unicode', 'parse_numeral']

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
# VULGAR_UNICODE_PATTERN = re.compile(r'([0-9])?([{}])(-)?'.format(''.join(p for p in VULGAR_UNICODE)))
NUMBER_PATTERN = re.compile(r'(?P<number>([,_]?[0-9])*)'
                            r'(\.(?P<decimal>[,_]?[0-9])*|\s?(?P<fraction>[0-9]+/[0-9]+))?')
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


_parse_numeral_pattern = re.compile(r'(?P<m>{})\b'.format(
    '|'.join(
        '|'.join([k.lower(), k.upper(), k.title()])
        for k in NUMERAL)), re.IGNORECASE)


def parse_numeral(s: str) -> str:
    """Converts numeral under 13 in string to number.

    Args:
        s (str): positional only. string to parse

    Examples:
        >>> parse_numeral('One to two cups parmesan')
        '1 to 2 cups parmesan'
        >>> parse_numeral('TEN BUCKS!')
        '10 BUCKS!'
        >>> parse_numeral('1234')
        '1234'
        >>> parse_numeral('something else ')
        'something else '
        >>> parse_numeral('tenderloin')
        'tenderloin'
    """
    def repl(m: Match):
        return str(NUMERAL[m.group('m').lower()])
    return _parse_numeral_pattern.sub(repl, s)


def parse_latex(s: str) -> str:
    """Converts simple LaTeX representation of a fraction to the valid literal

    Args:
        s (str): A given string to parse

    Returns:
        (str) A resultant string

    Examples:
        >>> parse_latex('\\frac{1}{2}')
        '1/2'
        >>> parse_latex('\\frac{4}{8}')
        '4/8'
        >>> parse_latex('\\frac{0}{1}')
        '0/1'
        >>> parse_latex('\\frac{3}{\\placeholder{denominator}}')
        '3'
    """
    pattern = re.compile('\frac{(.*?)}{(.*?)}')
    match = pattern.match(s)
    groups = list(match.groups())
    for number in groups:
        try:
            float(number)
        except ValueError:
            groups.remove(number)
    formatted = '{0}/{1}' if len(groups) > 1 else '{0}'
    return formatted.format(*groups) if match else s


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


def parse_fraction(s: str) -> 'Fraction':
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
        >>> parse_fraction('3.5') == Fraction(7, 2)
        True
    """
    try:
        numerator, denominator = map(float, s.split('/'))
        return Fraction(numerator, denominator)
    except ValueError:
        pass
    s = parse_vulgar_unicode(s)
    try:
        s = parse_latex(s)
    except AttributeError:
        pass
    try:
        numerator, denominator = map(float, s.split('/'))
        return Fraction(numerator, denominator)
    except ValueError as e:
        try:
            numerator = float(s)
            return Fraction(numerator)
        except ValueError as ee:
            raise ee from e


def parse_match(m: Match) -> 'Fraction':
    number = 0
    if m.group('number'):
        number = int(m.group('number'))
    if m.group('decimal'):
        assert not m.group('fraction')
        return Fraction(number + float(m.group('decimal')))
    if m.group('fraction'):
        assert not m.group('decimal')
        return parse_fraction(m.group('fraction')) + number
    return Fraction(number)


def parse_str(s: str) -> 'Fraction':
    """Converts a number string to Fraction.

    Also functions as an all-purpose converter to Fraction.

    Args:
        s (str): positional only. string to parse

    Examples;
        >>> parse_str('1/2') == Fraction(1, 2)
        True
        >>> parse_str('2 2/3') == Fraction(8, 3)
        True
        >>> parse_str('¼') == 0.25  # bad, call parse_vulgar_unicode first
        True
        >>> parse_str('¾') == 0.75  # bad, call parse_vulgar_unicode first
        True
        >>> parse_str('1½') == 1.5  # bad, call parse_vulgar_unicode first
        True
        >>> parse_str('3⅟100') == 3.01  # bad, call parse_vulgar_unicode first
        True
        >>> parse_str('1/8 1/8')
        Traceback (most recent call last):
          ...
        ValueError: Invalid fraction string '1/8 1/8'
        >>> parse_str('one eight')
        Traceback (most recent call last):
          ...
        ValueError: Invalid fraction string 'one eight'
    """
    if not isinstance(s, str):
        if isinstance(s, Fraction):
            return s
        if isinstance(s, int):
            return Fraction(s)
        if isinstance(s, float):
            return Fraction(s)
        if s.__class__.__name__ == 'Match':
            s = cast(Match, s)
            return parse_match(s)
        raise TypeError('Invalid type for fraction string \'{}\''
                        .format(s.__class__))
    try:
        if '/' in s:
            if ' ' in s:
                # ugly fraction
                parts = s.split(' ')
                n = len(parts)
                if n > 2:
                    raise NotImplementedError
                if n == 2:
                    number, fraction = parts
                    number = int(number)
                    fraction = parse_fraction(fraction)
                    return fraction + number
                raise AssertionError
            else:
                return parse_fraction(s)
        else:
            # maybe it's vulgar fraction
            new_s = parse_vulgar_unicode(s)
            if new_s != s:
                return parse_str(new_s)
            # not even fraction
            n = ''.join(s.split(' '))
            return Fraction(float(n))
    except ValueError:
        raise ValueError('Invalid fraction string \'{}\''
                         .format(s)) from None


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

    Notes:
        Doesn't support recurring decimals yet

    Examples:
        >>> to_ratio(5.6)
        (28, 5)
        >>> to_ratio(0.875)
        (7, 8)
        >>> to_ratio(-0.048)
        (-6, 125)
        >>> to_ratio(-3.6)
        (-18, 5)
        >>> to_ratio(math.inf)
        (1, 0)
        >>> to_ratio(math.nan)
        (0, 0)
        >>> to_ratio(1)
        (1, 1)
        >>> to_ratio(0.57)
        (57, 100)
        >>> to_ratio(2)
        (2, 1)
    """
    if math.isnan(x):
        return 0, 0
    if x == math.inf:
        return 1, 0
    if x == -math.inf:
        return -1, 0
    if isinstance(x, float):
        neg = False
        number, decimal = str(x).split('.')
        if number[0] == '-':
            number = number[1:]
            neg = True
        i = len(decimal)
        num = int(number) * 10 ** i + int(decimal)
        if neg:
            num = -num
        assert x == round(num / 10 ** i, 17), f'{x} != {round(num / 10 ** i, 17)}'
        return to_proper(num, 10 ** i)
    if isinstance(x, int):
        return x, 1


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

    __slots__ = ('numerator', 'denominator')

    def __init__(self, numerator, denominator=1):
        """Initialize a new fraction with the given numerator
           and denominator (default 1).

        Args:
            - numerator[, denominator=1] Union[int, float]
            - fraction_str (str)
        """
        if isinstance(numerator, int) and isinstance(denominator, int):
            self.numerator, self.denominator = to_proper(numerator, denominator)
        elif isinstance(numerator, float) or isinstance(denominator, float):
            frac = Fraction(*to_ratio(numerator)) / Fraction(*to_ratio(denominator))
            self.numerator, self.denominator = frac.numerator, frac.denominator
        elif isinstance(numerator, str) and denominator == 1:
            frac = parse_str(numerator)
            self.numerator, self.denominator = frac.numerator, frac.denominator
        else:
            raise TypeError("numerator must be 'int' or 'float'")
        assert isinstance(self.numerator, int)
        assert isinstance(self.denominator, int)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"{self.numerator}{f'/{self.denominator}' if self.denominator != 1 else ''}"

    def __int__(self):
        """Return the int representation of the fraction if possible."""
        if self.denominator == 1:
            return self.numerator
        raise ValueError('cannot convert \'{}\' to int'.format(self))

    def __float__(self):
        """Return the float representation of the fraction. 1/0 is considered as inf."""
        if self.is_infinite():
            sign = 1 if self.numerator > 0 else -1
            return sign * math.inf
        if self.isnan():
            return math.nan
        return self.numerator / self.denominator

    def __add__(self, other: Union[int, float, 'Fraction']) -> Union['Fraction', 'math.nan']:
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

    def __sub__(self, other: Union[int, float, 'Fraction']) -> Union['Fraction', 'math.nan']:
        if not isinstance(other, Fraction):
            if not isinstance(other, (int, float)):
                raise TypeError(type_error_msg_1(self, '-', other))
            other = Fraction(other)

        return self + (-other)

    def __mul__(self, other: Union[int, float, 'Fraction']) -> Union['Fraction', 'math.nan']:
        if not isinstance(other, Fraction):
            if not isinstance(other, (int, float)):
                raise TypeError(type_error_msg_1(self, '*', other))
            other = Fraction(other)

        return Fraction(self.numerator * other.numerator, self.denominator * other.denominator)

    def __truediv__(self, other: Union[int, float, 'Fraction']) -> Union['Fraction', 'math.nan']:
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

    def __gt__(self, other: 'Fraction'):
        if not isinstance(other, Fraction):
            if not isinstance(other, (int, float)):
                raise TypeError(type_error_msg_2(self, '>', other))
            other = Fraction(other)

        if self.isnan() or other.isnan():
            # nan cannot be ordered
            return False
        # avoids dividing because apparently multiplication is easier?
        return self.numerator * other.denominator > other.numerator * self.denominator

    def __lt__(self, other: 'Fraction'):
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

    def is_integer(self):
        return self.denominator == 1
