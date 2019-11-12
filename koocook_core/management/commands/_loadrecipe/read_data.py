import datetime
import enum
import json
import warnings
from pathlib import Path
from typing import List

from django.core.exceptions import ObjectDoesNotExist  # for .get()

from koocook.settings.dirs import BASE_DIR
from koocook_core import models
from koocook_core import support
from koocook_core.support import utils
from koocook_core.support import scripts

import datatrans.utils.structured_data
from datatrans import structured_data

DATA_DIR = BASE_DIR / 'data'


@enum.unique
class DataSet(enum.Enum):
    ALLRECIPES = DATA_DIR / 'allrecipes-recipes.json'
    BBCCOUK = DATA_DIR / 'bbccouk-recipes.json'
    COOKSTR = DATA_DIR / 'cookstr-recipes.json'
    EPICURIOUS = DATA_DIR / 'epicurious-recipes.json'


def read_data(data_set: DataSet, limit: int = 0) -> List[structured_data.Recipe]:
    with Path(data_set._value_).open('r', encoding='utf-8') as jsonfile:
        counter = 1
        recipes = []
        for line in jsonfile:
            data = json.loads(line)

            if data_set is DataSet.EPICURIOUS:
                d = {
                    'datePublished': structured_data.DateTime.fromisoformat(data['pubDate']),
                    'name': data['hed'],
                    'recipeInstructions': structured_data.Property(*data['prepSteps']),
                    'aggregateRating': structured_data.AggregateRating(
                        ratingValue=data['aggregateRating'],
                        reviewCount=data['reviewsCount']
                    )
                }

                if data['reviewsCount'] != 0:
                    d['aggregateRating'] = structured_data.AggregateRating(
                        ratingValue=data['aggregateRating'],
                        reviewCount=data['reviewsCount']
                    )

                if data['author']:
                    d['author'] = structured_data.Property(*[structured_data.Person(author['name'])
                                                             for author in data['author']])

                try:
                    d['recipeIngredient'] = structured_data.Property(*data['ingredients'])
                except KeyError as e:
                    warnings.warn('KeyError: {} in line#{}'.format(e, counter))
                    try:
                        if data['tag']['category'] == 'ingredient':
                            d['recipeIngredient'] = data['tag']['name']
                    except KeyError as e:
                        warnings.warn('KeyError: {} in line#{}'.format(e, counter))

                try:
                    if data['tag']['category'] == 'cuisine':
                        d['recipeCuisine'] = data['tag']['name']
                except KeyError as e:
                    warnings.warn('KeyError: {} in line#{}'.format(e, counter))
            ###########
            elif data_set is DataSet.ALLRECIPES:
                d = {
                    'author': structured_data.Person(data['author']),
                    'description': data['description'],
                    'recipeIngredient': structured_data.Property(*data['ingredients']),
                    'recipeInstructions': structured_data.Property(*data['instructions']),
                    'name': data['title']
                }
                if data['prep_time_minutes'] != 0 or data['cook_time_minutes'] != 0:
                    d['prepTime'] = structured_data.Duration(minutes=data['prep_time_minutes'])
                    d['cookTime'] = structured_data.Duration(minutes=data['cook_time_minutes'])
                if data['total_time_minutes'] != 0:
                    d['totalTime'] = structured_data.Duration(minutes=data['total_time_minutes'])
                if data['review_count']:
                    d['aggregateRating'] = structured_data.AggregateRating(
                        ratingValue=data['rating_stars'],
                        reviewCount=data['review_count']
                    )
            ###########
            elif data_set is DataSet.BBCCOUK:
                d = {
                    'author': structured_data.Person(data['chef']),
                    'recipeIngredient': structured_data.Property(*data['ingredients']),
                    'recipeInstructions': structured_data.Property(*data['instructions']),
                    'name': data['title']

                }
                if data['description']:
                    d['description'] = data['description']
                if data['preparation_time_minutes'] != 0 or data['cooking_time_minutes'] != 0:
                    d['prepTime'] = structured_data.Duration(minutes=data['preparation_time_minutes'])
                    d['cookTime'] = structured_data.Duration(minutes=data['cooking_time_minutes'])
                if data['total_time_minutes'] != 0:
                    d['totalTime'] = structured_data.Duration(minutes=data['total_time_minutes'])

                # TODO: Also include serving size 'serve' into the data

            ###########
            elif data_set is DataSet.COOKSTR:
                d = {
                    'cookingMethod': data['cooking_method'],
                    'datePublished': data['date_modified'],
                    'recipeIngredient': structured_data.Property(*data['ingredients']),
                    'recipeInstructions': structured_data.Property(*data['instructions']),
                    'name': data['title']
                }
                if data['chef']:
                    d['author'] = structured_data.Person(data['chef'])
                if data['description']:
                    d['description'] = data['description']
                if data['rating_count']:
                    d['aggregateRating'] = structured_data.AggregateRating(
                        ratingValue=data['rating_value'],
                        ratingCount=data['rating_count']
                    )

            recipe = structured_data.Recipe(
                **d,
                suppress=True
            )

            recipes.append(recipe)
            counter += 1
            if limit:
                if counter > limit:
                    break

    return recipes


def parse_cooking_method(cooking_method: str) -> models.Tag:
    """ Returns a ``Tag`` for the cooking method. Creates a new one if DNE. """
    try:
        label = models.TagLabel.objects.filter(name__iexact='cooking method').get()
    except ObjectDoesNotExist:
        label = models.TagLabel.objects.create(name='cooking method')
    # don't catch MultipleObjectsReturned

    try:
        tag = models.Tag.objects.filter(name__iexact=cooking_method, label=label).get()
    except ObjectDoesNotExist:
        tag = models.Tag.objects.create(name=cooking_method, label=label)
    # don't catch MultipleObjectsReturned

    return tag


def parse_ingredients(ingredients: structured_data.Property) -> List[models.RecipeIngredient]:
    recipeingredients = []
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
                warnings.warn('Found no matching meta ingredient, trying FoodDataAPI')
                nutrients, name = support.scripts.get_nutrients(description)
                meta = models.MetaIngredient(name=name, nutrients=nutrients)
                meta.save()
                # parts = meta_str.split(' ')
                # if len(parts) == 1:
                #     meta = models.MetaIngredient.objects.create(name=meta_str, nutrients={})
                # elif len(parts) < 3:
                #     warnings.warn('Found no matching meta ingredient. '
                #                   'Creating new meta ingredient \'{}\''
                #                   .format(meta_str))
                #     meta = models.MetaIngredient.objects.create(name=meta_str, nutrients={})
                # else:
                #     warnings.warn('Found no matching meta ingredient. '
                #                   'Creating new meta ingredient \'{}\''
                #                   .format(meta_str))
                #     meta = models.MetaIngredient.objects.create(name=meta_str, nutrients={})
                #     # raise ValueError('Found no matching meta ingredient.'
                #     #                  'Please defer ingredient creation.')
        # don't catch MultipleObjectsReturned
        recipeingredients.append(models.RecipeIngredient.objects.create(description=description, quantity=quantity, meta=meta))
    return recipeingredients


def parse_instructions(instructions: structured_data.Property) -> List[str]:
    return list(instructions)


def parse_author(author: structured_data.Person) -> models.Author:
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
    d = datetime.datetime.fromisoformat(str(datetime_str))
    return d


def parse_recipe(recipe: structured_data.Recipe) -> models.Recipe:
    skip = False
    data = {}
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

    later = {}
    for k, v, f in (
            ('_recipe_ingredient', 'recipeingredient_set', parse_ingredients),
            ('_cooking_method', 'tag_set', parse_cooking_method),
            # ('', 'tag_set', None),
            # ('', 'comment_set', None),
    ):
        try:
            if getattr(recipe, k) is not None:
                if f is not None:
                    later[v] = f(getattr(recipe, k))
                else:
                    later[v] = getattr(recipe, k)
        except ResourceWarning:
            skip = True
    if not hasattr(data, 'aggregate_rating'):
        data['aggregate_rating'] = models.AggregateRating.objects.create(
            rating_value=0, rating_count=0
        )

    if not skip:
        r = models.Recipe(**data)
        r.save()

        for ingr in later['recipeingredient_set']:
            r.recipeingredient_set.add(ingr)
        try:
            r.tag_set.add(later['tag_set'])
        except KeyError:
            pass

        return r
    return


def main():
    recipes = read_data(DataSet.COOKSTR, 10)
    for recipe in recipes:
        parse_recipe(recipe)
    print(json.dumps(recipes, default=datatrans.utils.json_encoder))


if __name__ == '__main__':
    main()
