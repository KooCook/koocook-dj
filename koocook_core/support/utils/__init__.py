import datetime

from koocook_core.support import fraction
from koocook_core.support import unit

try:
    import datatrans.utils
except ModuleNotFoundError:
    pass


def split_ingredient_str(s: str) -> ('fraction.Fraction', 'unit.Unit', str):
    """

    Examples:
        >>> split_ingredient_str('1 1/2 large onions, finely sliced')
        (3/2, <SpecialUnit.NONE: ''>, 'large onions, finely sliced')
        >>> split_ingredient_str('One 10-inch-long beef tenderloin roast cut from the heart of the tenderloin (2\\u00bd to 3 pounds), butterflied (see Note)')
        (1, <SpecialUnit.NONE: ''>, '10-inch-long beef tenderloin roast cut from the heart of the tenderloin (2½ to 3 pounds), butterflied (see Note)')
        >>> split_ingredient_str('4 ounces thinly sliced salami, cut into \\u00bc-inch-wide matchsticks')
        (4, <MassUnit.OUNCE: 'oz'>, 'thinly sliced salami, cut into ¼-inch-wide matchsticks')
        >>> split_ingredient_str('2 garlic cloves, finely minced')
        (2, <SpecialUnit.NONE: ''>, 'garlic cloves, finely minced')
        >>> split_ingredient_str('One plus 3 tablespoons extra virgin olive oil')
        (4, <VolumeUnit.TABLESPOON: 'tbsp'>, 'extra virgin olive oil')
        >>> split_ingredient_str('8-9 ounces fresh spinach')
        (17/2, <MassUnit.OUNCE: 'oz'>, 'fresh spinach')
        >>> split_ingredient_str('1 to 2 canned chipotle chiles en adobo, stemmed and seeded')
        (3/2, <SpecialUnit.NONE: ''>, 'canned chipotle chiles en adobo, stemmed and seeded')
        >>> split_ingredient_str('1 to 2 tablespoons chipotle canning sauce')
        (3/2, <VolumeUnit.TABLESPOON: 'tbsp'>, 'chipotle canning sauce')
    """
    s = fraction.parse_numeral(s)
    s = fraction.parse_vulgar_unicode(s)
    numbers = []
    spans = []
    for m in fraction.NUMBER_PATTERN.finditer(s):
        if m.group():
            numbers.append(fraction.parse_match(m))
            spans.append((m.start(), m.end()))
    if len(numbers) > 1:
        if 'plus' in s[spans[0][0]:spans[1][1]]:
            number = numbers[0] + numbers[1]
            rest = s[spans[1][1]:]
        elif 'to' in s[spans[0][1]:spans[1][0]]:
            number = (numbers[0] + numbers[1]) / 2
            rest = s[spans[1][1]:]
        elif '-' in s[spans[0][1]:spans[1][0]]:
            number = (numbers[0] + numbers[1]) / 2
            rest = s[spans[1][1]:]
        else:
            number = numbers[0]
            rest = s[spans[0][1]:]
    else:
        try:
            number = numbers[0]
            rest = s[spans[0][1]:]
        except IndexError as e:
            # raise ValueError('cannot parse w/o amount string \'{}\''
            #                  .format(s)) from e.__context__
            number = fraction.Fraction(0)
            rest = s

    parts = rest.split(' ')
    parts.pop(0)  # remove first ['', ...]
    try:
        unit_part = unit.get_unit(parts[0])
        parts.pop(0)
    except ValueError:
        unit_part = unit.SpecialUnit.NONE
    except IndexError:
        unit_part = unit.SpecialUnit.NONE

    description = ' '.join(parts)
    return number, unit_part, description
=======
import datetime


def split_ingredient_str(string: str) -> List[str]:
    """

    # Examples:
    #     >>> split_ingredient_str('1 1/2 large onions, finely sliced')
    #     [1.5, '', 'large onions, finely sliced']
    #     >>> split_ingredient_str('One 10-inch-long beef tenderloin roast cut from the heart of the tenderloin (2\\u00bd to 3 pounds), butterflied (see Note)')
    #     [1, '', '10-inch-long beef tenderloin roast cut from the heart of the tenderloin (2½ to 3 pounds), butterflied (see Note)']
    #     >>> split_ingredient_str('4 ounces thinly sliced salami, cut into \\u00bc-inch-wide matchsticks')
    #     [4, 'ounces', 'thinly sliced salami, cut into ¼-inch-wide matchsticks']
    #     >>> split_ingredient_str('2 garlic cloves, finely minced')
    #     [2, '', 'garlic cloves, finely minced']
    #     >>> split_ingredient_str('One plus 3 tablespoons extra virgin olive oil')
    #     [4, 'tablespoons', 'extra virgin olive oil']
    #     >>> split_ingredient_str('8-9 ounces fresh spinach')
    #     ['8-9', 'ounces', 'fresh spinach']
    #     >>> split_ingredient_str('to 2 canned chipotle chiles en adobo, stemmed and seeded')
    #     ['1 to 2', '', 'canned chipotle chiles en adobo, stemmed and seeded']
    #     >>> split_ingredient_str('1 to 2 tablespoons chipotle canning sauce')
    #     ['1 to 2', 'tablespoons', 'chipotle canning sauce']
    """
    number_part = []
    unit_part = None
    ingredient_part = []
    number_end = False
    unit_end = False
    for part in string.split(' '):
        if not number_end:
            try:
                number = float(part)
            except ValueError as e:
                pass
            try:
                number = datatrans.utils.parse_vulgar_fractions(part)
            except ValueError as e:
                pass
            try:
                number = datatrans.utils.parse_numeral(part)
            except ValueError as e:
                pass
            try:
                number_part.append(number)
                del number
                continue
            except UnboundLocalError:
                if part.lower() not in (
                    'plus',
                    'and',
                ):
                    number_end = True
                else:
                    continue
        if not unit_end:
            try:
                unit.get_unit(part)
                unit_part = part
                continue
            except ValueError:
                pass
            unit_end = True
        ingredient_part.append(part)
    number = sum(number_part)
    if isinstance(number, float) and number.is_integer():
        number = int(number)
    return [number, unit_part if unit_part is not None else '', ' '.join(ingredient_part)]


def get_prep_cook_times(prep_time: datetime.timedelta = None,
                        cook_time: datetime.timedelta = None,
                        total_time: datetime.timedelta = None
                        ) -> (datetime.timedelta, datetime.timedelta):
    """Given some times, return ``prep_time`` and ``cook_time``.

    >>> get_prep_cook_times(total_time=datetime.timedelta(minutes=20), prep_time=datetime.timedelta(minutes=5))
    (datetime.timedelta(seconds=300), datetime.timedelta(seconds=900))
    >>> get_prep_cook_times(total_time=datetime.timedelta(minutes=5), prep_time=datetime.timedelta(seconds=30))
    (datetime.timedelta(seconds=30), datetime.timedelta(seconds=270))
    """
    if prep_time and cook_time:
        return prep_time, cook_time
    if None not in (prep_time, cook_time):
        return prep_time, cook_time
    if total_time is not None:
        if prep_time is not None:
            return prep_time, total_time - prep_time
        elif cook_time is not None:
            return total_time - cook_time, cook_time
        else:
            return None, total_time
    # total_time is None and one of the two times is also None
    # Guessing at this point
    return None, prep_time or cook_time


if __name__ == '__main__':
    import doctest
    doctest.testmod()
