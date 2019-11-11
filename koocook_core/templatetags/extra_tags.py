from django import template

register = template.Library()

# register.filter(lambda x: x // 3600, name='hours')
@register.filter()
def hours(seconds):
    hour = seconds // 3600
    if hour > 1:
        return f'{hour} hrs'
    else:
        return '1 hr'


@register.filter()
def minutes(seconds):
    if seconds >= 3600:
        seconds /= 60
    minute = seconds // 60
    if minute > 1:
        return f'{minute} mins'
    else:
        return '1 min'


@register.filter
def to_int(value):
    return int(value)


@register.filter
def rating(value):
    return f'{value:.1f}'
