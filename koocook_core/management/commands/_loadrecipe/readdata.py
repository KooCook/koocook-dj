import enum
import json
import warnings
from pathlib import Path
from typing import List

from datatrans import structured_data

from koocook.settings.dirs import DATA_DIR


@enum.unique
class DataSet(enum.Enum):
    ALLRECIPES = DATA_DIR / 'allrecipes-recipes.json'
    BBCCOUK = DATA_DIR / 'bbccouk-recipes.json'
    COOKSTR = DATA_DIR / 'cookstr-recipes.json'
    EPICURIOUS = DATA_DIR / 'epicurious-recipes.json'


def read_allrecipes_data(data: dict, *args) -> dict:
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
    return d


def read_bbccouk_data(data: dict, *args) -> dict:
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
    return d


def read_cookstr_data(data: dict, *args) -> dict:
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
    return d


def read_epicurious_data(data: dict, counter: int) -> dict:
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
    return d


def read_data(data_set: DataSet, limit: int = 0) -> List[structured_data.Recipe]:
    with Path(data_set._value_).open('r', encoding='utf-8') as jsonfile:
        counter = 1
        recipes = []
        for line in jsonfile:
            data = json.loads(line)

            d = {
                DataSet.ALLRECIPES: read_allrecipes_data,
                DataSet.BBCCOUK: read_bbccouk_data,
                DataSet.COOKSTR: read_cookstr_data,
                DataSet.EPICURIOUS: read_epicurious_data,
            }[data_set](data, counter)

            recipe = structured_data.Recipe(**d, suppress=True)
            recipes.append(recipe)
            counter += 1
            if limit:
                if counter > limit:
                    break

    return recipes
