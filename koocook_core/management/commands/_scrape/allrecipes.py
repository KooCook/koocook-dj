import datetime
from typing import List
import time

import datatrans.utils.structured_data
from django.core.exceptions import ObjectDoesNotExist  # for .get()

from koocook_core import models
from koocook_core import support
from koocook_core.support import scripts
from koocook_core.support import utils

from koocook_core.models import Recipe, AggregateRating, Author, MetaIngredient, RecipeIngredient

import isodate
import requests
from bs4 import BeautifulSoup


def get_aggr(soup: BeautifulSoup) -> AggregateRating:
    aggr: BeautifulSoup = soup.find(**{'class': 'aggregate-rating'})
    rating_value = aggr.find(itemprop='ratingValue')['content']
    rating_count = aggr.find(itemprop='reviewCount')['content']
    return AggregateRating.objects.create(rating_value=rating_value, rating_count=rating_count)


def get_name(soup: BeautifulSoup) -> str:
    return soup.find(id='recipe-main-content').string


def get_author(soup: BeautifulSoup) -> Author:
    author_str = soup.find(itemprop='author').string
    try:
        return Author.objects.get(name=author_str)
    except Author.DoesNotExist:
        return Author.objects.create(name=author_str)


def get_img(soup: BeautifulSoup) -> List[str]:
    imgs = set()
    for elem in soup.find(**{'class': 'hero-photo__image'}).find_all('img'):
        imgs.add(elem['src'])
    return list(imgs)


def get_instructions(soup: BeautifulSoup) -> List[str]:
    instrs = []
    for elem in soup.find(itemprop='recipeInstructions').find_all(**{'class': 'step'}):
        instrs.append(elem.span.string)
    return instrs


def get_description(soup: BeautifulSoup) -> str:
    return soup.find('div', itemprop='description').string.split('"')[1]


def get_prep_time(soup: BeautifulSoup) -> datetime.timedelta:
    return isodate.parse_duration(soup.find('time', itemprop='prepTime')['datetime'])


def get_cook_time(soup: BeautifulSoup) -> datetime.timedelta:
    return isodate.parse_duration(soup.find('time', itemprop='cookTime')['datetime'])


def add_ingr(soup: BeautifulSoup, recipe: Recipe) -> None:
    for span in soup.find(id='lst_ingredients_1').find_all(itemprop='recipeIngredient'):
        ingr_str: str = span.string
        '3 cups all-purpose flour'
        number, unit, description = utils.split_ingredient_str(ingr_str)
        quantity = support.Quantity(number, unit)
        try:
            meta = MetaIngredient.objects.filter(name__iexact=description).get()
        except ObjectDoesNotExist:
            meta = MetaIngredient.objects.create(name=description)
        # don't catch MultipleObjectsReturned
        models.RecipeIngredient.objects.create(description=description, quantity=quantity, meta=meta, recipe=recipe)


def parse_detail_soup(soup: BeautifulSoup):
    recipe = Recipe()
    recipe.name = get_name(soup)
    recipe.aggregate_rating = get_aggr(soup)
    recipe.author = get_author(soup)
    recipe.image = get_img(soup)
    recipe.description = get_description(soup)
    recipe.recipe_instructions = get_instructions(soup)
    recipe.prep_time = get_prep_time(soup)
    recipe.cook_time = get_cook_time(soup)
    recipe.save()
    add_ingr(soup, recipe)


def main():
    url = 'https://www.allrecipes.com/recipe/255937/glendas-gingerbread-pancakes/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    parse_detail_soup(soup)
