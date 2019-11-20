from django import template

register = template.Library()


@register.filter(name='tag_level')
def tag_level(label):
    level = {1: 'is-white', 2: 'is-success', 3: 'is-warning', 4: 'is-danger'}
    return level.get(label)
