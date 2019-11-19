from django import template

register = template.Library()


@register.filter(name='top_latest')
def top_latest_recipes(recipes):
    return recipes.order_by('-date_published', 'aggregate_rating')[:10]
