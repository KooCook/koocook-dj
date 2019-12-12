from typing import List
import warnings

from django.core.exceptions import ObjectDoesNotExist  # for .get()

from koocook_core.support import utils, parse_quantity, Quantity
from koocook_core.models import Recipe, AggregateRating, Author, MetaIngredient, RecipeIngredient, Tag

import requests
from bs4 import BeautifulSoup


def get_search_view(page: int = 1) -> str:
    if page != 1:
        return f'https://www.epicurious.com/search?content=recipe&page={page}'
    return 'https://www.epicurious.com/search?content=recipe'


def get_links(soup: BeautifulSoup) -> List[str]:
    """ Get links from search view soup """
    out = []
    for a in soup.find_all('a', **{'class': 'view-complete-item', 'itemprop':'url'}):
        out.append('https://www.epicurious.com' + a['href'])
    return out


def parse_detail_soup(soup: BeautifulSoup) -> None:
    recipe = Recipe()
    recipe.name = get_name(soup)
    recipe.author = get_author(soup)
    recipe.aggregate_rating = get_aggr(soup)
    recipe.image = get_image(soup)
    try:
        recipe.description = get_description(soup)
    except AttributeError:
        pass
    recipe.recipe_instructions = get_instructions(soup)
    try:
        recipe.recipe_yield = get_yield(soup)
    except AttributeError:
        pass
    recipe.save()
    add_ingr(soup, recipe)
    add_tags(soup, recipe)


def get_name(soup: BeautifulSoup) -> str:
    return soup.find('h1', itemprop='name').string


def get_author(soup: BeautifulSoup) -> Author:
    author_str = soup.find('a', itemprop='author').string
    try:
        return Author.objects.get(name=author_str)
    except Author.DoesNotExist:
        return Author.objects.create(name=author_str)


def get_aggr(soup: BeautifulSoup) -> AggregateRating:
    aggr: BeautifulSoup = soup.find(itemprop='aggregateRating')
    best_rating = aggr.find(itemprop='bestRating')['content']
    if best_rating != '4':
        raise AssertionError(f'{best_rating}')
    worst_rating = aggr.find(itemprop='worstRating')['content']
    if worst_rating != '0':
        raise AssertionError(f'{worst_rating}')
    rating_value = float(aggr.find(itemprop='ratingValue')['content'])
    rating_value += 1  # 0-4 -> 1-5
    rating_count = int(aggr.find(itemprop='reviewCount').string)
    return AggregateRating.objects.create(rating_value=rating_value, rating_count=rating_count)


def get_image(soup: BeautifulSoup) -> List[str]:
    return [soup.find('picture').source['srcset']]


def get_description(soup: BeautifulSoup) -> str:
    return soup.find(itemprop='description').string.strip()


def get_instructions(soup: BeautifulSoup) -> List[str]:
    out = []
    for li in soup.find(itemprop='recipeInstructions').ol.find_all('li', **{'class': 'preparation-step'}):
        try:
            out.append(li.string.strip())
        except AttributeError:
            if len(out) > 0:
                pass
            else:
                raise
    return out


def strip_number(s: str) -> int:
    num_str = ''.join(c for c in s if c in '1234567890')
    return int(num_str.replace('.', ''))


def get_yield(soup: BeautifulSoup) -> 'Quantity':
    serving_str = soup.find(itemprop='recipeYield').string.strip()
    '8 servings'
    'Makes about 60'
    try:
        return parse_quantity(serving_str)
    except ValueError:
        warnings.warn(f"cannot parse yield '{serving_str}', skipping")


def add_ingr(soup: BeautifulSoup, recipe: Recipe) -> None:
    for li in soup.find_all(itemprop='ingredients'):
        ingr_str = li.string
        '8 small sweet potatoes (about 3 lb. total), scrubbed, halved lengthwise'
        number, unit, description = utils.split_ingredient_str(ingr_str)
        quantity = Quantity(number, unit)
        try:
            meta = MetaIngredient.objects.filter(name__iexact=description).get()
        except ObjectDoesNotExist:
            meta = MetaIngredient.objects.create(name=description)
        # don't catch MultipleObjectsReturned
        RecipeIngredient.objects.create(description=description, quantity=quantity, meta=meta, recipe=recipe)


def add_tags(soup: BeautifulSoup, recipe: Recipe) -> None:
    for dt in soup.find(**{'class': 'tags'}).find_all(itemprop='recipeCategory'):
        tag_str = dt.string
        'Bon Appétit'
        try:
            tag = Tag.objects.filter(name__iexact=tag_str).get()
        except ObjectDoesNotExist:
            tag = Tag.objects.create(name=tag_str)
            warnings.warn(f"creating new tag with no label: '{tag}'")
        # don't catch MultipleObjectsReturned
        recipe.tag_set.add(tag)


def main(num):
    """ Scrape ``num`` recipes from epicurious.com """
    links = []
    count = 0
    page = 1
    while count < num:
        try:
            link = links.pop(-1)
        except IndexError:
            res = requests.get(get_search_view(page))
            soup = BeautifulSoup(res.text, 'html.parser')
            links.extend(get_links(soup))
            page += 1
            continue
        res = requests.get(link)
        soup = BeautifulSoup(res.text, 'html.parser')
        parse_detail_soup(soup)
        count += 1
