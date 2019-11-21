import datetime
from typing import List, Sequence, Optional
import time

import datatrans.utils.structured_data
from datatrans import structured_data
from django.core.exceptions import ObjectDoesNotExist  # for .get()

from koocook_core import models
from koocook_core import support
from koocook_core.support import scripts
from koocook_core.support import utils
from .readdata import read_data, DataSet


def parse_cooking_method(cooking_method: str) -> List[models.Tag]:
    """ Returns a ``Tag`` for the cooking method. Creates a new one if DNE. """
    try:
        label = models.TagLabel.objects.filter(name__iexact='cooking method').get()
    except ObjectDoesNotExist:
        label = models.TagLabel.objects.create(name='cooking method')
    # don't catch MultipleObjectsReturned
    methods = cooking_method.split(', ')
    tags: List[models.Tag] = []
    for method in methods:
        try:
            tag = models.Tag.objects.filter(name__iexact=method, label=label).get()
        except ObjectDoesNotExist:
            tag = models.Tag.objects.create(name=method, label=label)
        # don't catch MultipleObjectsReturned
        tags.append(tag)

    return tags


def parse_ingredients(ingredients: structured_data.Property, r: models.Recipe) -> List[models.RecipeIngredient]:
    recipeingredients: List[models.RecipeIngredient] = []
    for ingredient in ingredients:
        number, unit, description = utils.split_ingredient_str(ingredient)
        if unit != '':
            unit = support.get_unit(unit)
        else:
            unit = support.SpecialUnit.NONE
        quantity = support.Quantity(number, unit)
        try:
            # try exact match
            meta = models.MetaIngredient.objects.filter(name__iexact=description).get()
        except ObjectDoesNotExist:
            # try contains
            names = {meta.name: meta for meta in models.MetaIngredient.objects.all()}
            match = datatrans.utils.get_closest_match(description, names.keys())
            if match is not None:
                meta = models.MetaIngredient.objects.filter(name__exact=match).get()
            else:
                # go for FoodData API
                try:
                    nutrients, name = support.scripts.get_nutrients(description)
                    # so we don't get flagged for ddos
                    time.sleep(1)
                except KeyError as e:
                    raise ResourceWarning from e
                try:
                    meta = models.MetaIngredient.objects.get(name__exact=name)
                except ObjectDoesNotExist:
                    meta = models.MetaIngredient.objects.create(name=name, nutrient=nutrients)
        # don't catch MultipleObjectsReturned
        recipeingredients.append(
            models.RecipeIngredient.objects.create(description=description, quantity=quantity, meta=meta, recipe=r))
    return recipeingredients


def parse_instructions(instructions: structured_data.Property) -> List[str]:
    return list(instructions)


def parse_author(author: structured_data.Person) -> models.Author:
    if isinstance(author, Sequence):
        author = author[0]
    try:
        try:
            author = models.Author.objects.filter(name__iexact=author._name).get()
        except AttributeError:
            author = models.Author.objects.filter(name__iexact=author[0]._name).get()
    except ObjectDoesNotExist:
        try:
            author = models.Author.objects.create(name=author._name)
        except AttributeError:
            author = models.Author.objects.create(name=author[0]._name)
    # Don't catch MultipleObjectsReturned
    return author


def parse_aggregate_rating(aggregate_rating: structured_data.AggregateRating) -> models.AggregateRating:
    kwargs = {
        'rating_value': aggregate_rating._rating_value,
        'rating_count': aggregate_rating._rating_count,
    }
    if kwargs['rating_count'] is None:
        kwargs['rating_count'] = 1
    if kwargs['rating_value'] is None:
        kwargs['rating_value'] = 0

    if aggregate_rating._best_rating is not None:
        kwargs['best_rating'] = aggregate_rating._best_rating
    if aggregate_rating._worst_rating is not None:
        kwargs['best_rating'] = aggregate_rating._worst_rating
    return models.AggregateRating.objects.create(**kwargs)


def parse_datetime(datetime_str: str):
    return datetime.datetime.fromisoformat(str(datetime_str))


def parse_recipe(recipe: structured_data.Recipe) -> Optional[models.Recipe]:
    skip = False
    data = {}
    r = models.Recipe(name='', recipe_instructions=[])

    for k, v, f in (
            ('_name', 'name', None),
            ('_image', 'video', None),
            ('_video', 'name', None),
            ('_author', 'author', parse_author),
            ('_date_published', 'date_published', parse_datetime),
            ('_description', 'description', None),
            ('_recipe_instructions', 'recipe_instructions', parse_instructions),
            ('_recipe_yield', 'recipe_yield', None),
            ('_aggregate_rating', 'aggregate_rating', parse_aggregate_rating),
            ('_cooking_method', 'tag_set', parse_cooking_method),
    ):
        try:
            if getattr(recipe, k) is not None:
                if f is not None:
                    data[v] = f(getattr(recipe, k))
                else:
                    data[v] = getattr(recipe, k)
        except ResourceWarning:
            skip = True

    data['prep_time'], data['cook_time'] = utils.get_prep_cook_times(
        prep_time=data.get('prep_time', None),
        cook_time=data.get('cook_time', None),
        total_time=data.get('total_time', None)
    )

    r.update(dct=data)
    data = {}

    try:
        data['recipeingredient_set'] = parse_ingredients(getattr(recipe, '_recipe_ingredient'), r)
    except ResourceWarning:
        skip = True

    if not skip:
        r.update(dct=data)
        return r
    return


def main():
    recipes = read_data(DataSet.COOKSTR, 10)
    for recipe in recipes:
        parse_recipe(recipe)
    # print(json.dumps(recipes, default=datatrans.utils.json_encoder))


if __name__ == '__main__':
    main()
