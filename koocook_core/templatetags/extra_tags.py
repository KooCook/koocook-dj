from django import template

register = template.Library()


@register.filter
def hours(seconds):
    hour = seconds // 3600
    if hour > 1:
        return f'{hour} H'
    else:
        return '1 H'


@register.filter
def minutes(seconds):
    if seconds >= 3600:
        seconds %= 3600
    minute = seconds // 60
    if minute > 1:
        return f'{minute} M'
    elif minute == 1:
        return '1 M'
    else:
        return ''


@register.filter
def to_int(value):
    return int(value)


@register.filter
def rating(value):
    return f'{value:.1f}'


@register.filter
def time_bar(second):
    minute = second / 60
    if minute < 60:
        return minute / 10
    else:
        return 6
