from django import template

register = template.Library()


@register.filter(name='top_latest')
def top_latest_recipes(recipes):
    filter_recipes = list(recipes.order_by('date_published')[:10])
    filter_recipes.sort(key=lambda recipe: recipe.aggregate_rating, reverse=True)
    return filter_recipes
