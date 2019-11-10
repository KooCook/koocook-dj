from django import template

register = template.Library()

register.simple_tag(lambda x: x // 3600, name='hours')


@register.simple_tag()
def minutes(seconds):
    if seconds >= 3600:
        seconds /= 60
    return seconds // 60
