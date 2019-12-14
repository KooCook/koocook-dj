import datetime
from typing import List, Union
import itertools

from django.core.exceptions import ObjectDoesNotExist  # for .get()

from koocook_core.support import utils, Quantity, unit

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
    return soup.find(itemprop='name', id='recipe-main-content').string


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
    iterables = itertools.chain(*[soup.find(id=_).find_all(itemprop='recipeIngredient') for _ in ('lst_ingredients_1', 'lst_ingredients_2')])
    for span in iterables:
        ingr_str: str = span.string
        '3 cups all-purpose flour'
        number, unit, description = utils.split_ingredient_str(ingr_str)
        quantity = Quantity(number, unit)
        try:
            meta = MetaIngredient.objects.filter(name__iexact=description).get()
        except ObjectDoesNotExist:
            meta = MetaIngredient.objects.create(name=description)
        # don't catch MultipleObjectsReturned
        RecipeIngredient.objects.create(description=description, quantity=quantity, meta=meta, recipe=recipe)


def get_yield(soup: BeautifulSoup) -> Quantity:
    servings = int(soup.find(itemprop='recipeYield')['content'])
    return Quantity(servings, unit.SpecialUnit.SERVING)


def parse_detail_soup(soup: BeautifulSoup) -> None:
    recipe = Recipe()
    recipe.name = get_name(soup)
    recipe.aggregate_rating = get_aggr(soup)
    recipe.author = get_author(soup)
    recipe.image = get_img(soup)
    recipe.description = get_description(soup)
    recipe.recipe_instructions = get_instructions(soup)
    recipe.prep_time = get_prep_time(soup)
    recipe.cook_time = get_cook_time(soup)
    recipe.recipe_yield = get_yield(soup)
    recipe.save()
    add_ingr(soup, recipe)


def get_links(url: str) -> List[str]:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    nums = set()
    for elem in soup.find_all('a'):
        try:
            link = elem['href']
            if 'https://www.allrecipes.com/recipe/' in link:
                try:
                    num = link.split('/')[4]
                    if len(num) > 4:
                        nums.add(num)
                except IndexError:
                    pass
        except KeyError:
            pass
    return list(nums)


def scrape(id_: Union[int, str]):
    """ Scrape recipe with id ``id`` """
    response = requests.get(f'https://www.allrecipes.com/recipe/{id_}/')
    soup = BeautifulSoup(response.text, 'html.parser')
    try:
        parse_detail_soup(soup)
    except AttributeError:
        pass
    except TypeError:
        pass


def main(num: int, page: int = 1):
    """ Scrape ``num`` recipes from allrecipes.com """
    count = 0
    i = page - 1
    urls = get_links(f'https://www.allrecipes.com/{f"?page={i + 1}" if i else ""}')
    while count < num:
        try:
            scrape(urls.pop(-1))
        except IndexError:
            i += 1
            urls = get_links(f'https://www.allrecipes.com/{f"?page={i + 1}" if i else ""}')
            scrape(urls.pop(-1))
        count += 1
