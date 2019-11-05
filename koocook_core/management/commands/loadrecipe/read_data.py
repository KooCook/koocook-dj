from typing import List

import enum
import json
from pathlib import Path
import warnings

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned  # for .get()

from datatrans import structured_data
import datatrans.utils.structured_data
from koocook.settings.dirs import BASE_DIR
import koocook_core.models as models
import koocook_core.support as support

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


def main():
    recipes = read_data(DataSet.COOKSTR, 10)

    print(json.dumps(recipes, default=datatrans.utils.structured_data.default))


if __name__ == '__main__':
    main()
