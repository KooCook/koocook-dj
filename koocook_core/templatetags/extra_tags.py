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


@register.filter(name='to_h_m')
def print_time(seconds):
    if seconds == 0:
        return '-'

    result = f''
    if seconds >= 3600:
        hour = seconds // 3600
        seconds %= 3600
    else:
        hour = 0

    if seconds >= 60:
        minute = seconds // 60
    else:
        minute = 1

    if hour >= 1:
        result += f'{hour} H'
    if minute >= 1:
        result += f'{minute} M'
    return result


@register.filter
def to_int(value):
    return int(value)


@register.filter
def rating(value):
    return f'{float(value):.1f}' if value else f'{0:.1f}'


@register.filter
def time_bar(second):
    minute = second / 60
    if minute < 60:
        return minute / 10
    else:
        return 6
