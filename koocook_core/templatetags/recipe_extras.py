import datetime
from django import template

register = template.Library()


@register.filter(name='tag_level')
def tag_level(lv: int) -> str:
    """ Return Bulma color helper by given label_level """
    level = {1: 'is-info', 2: 'is-success', 3: 'is-warning', 4: 'is-danger'}
    return level.get(lv)


@register.filter(name='timedel_to_words')
def duration_in_words(duration: datetime.timedelta) -> str:
    """Converts a timedelta duration to a word

    Args:
        duration (datetime.timedelta): A given duration

    Returns:
        (str) A timedelta duration in word representation
    """
    def plural(n):
        return n, abs(n) != 1 and "s" or ""
    mm, ss = divmod(duration.seconds, 60)
    hh, mm = divmod(mm, 60)
    s = ''
    if ss:
        s = ("%d second%s " % plural(ss)) + s
    if mm:
        s = ("%d minute%s " % plural(mm)) + s
    if hh:
        s = ("%d hour%s " % plural(hh)) + s
    if duration.days:
        s = ("%d day%s, " % plural(duration.days)) + s
    return s
