from django.contrib.postgres import fields
from django.db import models

from koocook_core import fields as koocookfields
from .review import ReviewableModel

__all__ = ['Recipe']


class Recipe(ReviewableModel, models.Model):
    """

    Note:
        - description = models.CharField(max_length=255)
        - recipeingredient_set from Ingredient's ForeignKey
        - comment_set from Comment's ForeignKey
    """
    name = models.CharField(max_length=255)
    image = fields.ArrayField(models.CharField(max_length=200), null=True)
    video = models.URLField(null=True, blank=True)
    author = models.ForeignKey(
        'koocook_core.Author',
        on_delete=models.PROTECT,
        null=True,
    )
    date_published = models.DateTimeField(null=True, auto_now_add=True)
    description = models.TextField()
    prep_time = models.DurationField(null=True, blank=True)
    cook_time = models.DurationField(null=True)
    recipe_instructions = fields.ArrayField(models.TextField())
    recipe_yield = koocookfields.QuantityField(null=True)
    tag_set = models.ManyToManyField('koocook_core.Tag', blank=True)
    aggregate_rating = models.OneToOneField(
        'koocook_core.AggregateRating',
        on_delete=models.PROTECT,
        blank=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # if not hasattr(self, 'aggregate_rating'):
        #     self.aggregate_rating = create_empty_aggregate_rating()

    @property
    def total_time(self):
        return self.prep_time + self.cook_time

    @property
    def nutrition(self):
        nutrition_list = []
        for ingredient in self.recipe_ingredients:
            for nutrient in ingredient.nutrition:
                if nutrient['nutrient'] not in list(map(lambda x: x['nutrient'], nutrition_list)):
                    nutrition_list.append(nutrient)
                else:
                    for i in range(len(nutrition_list)):
                        if nutrition_list[i]['nutrient'] == nutrient['nutrient']:
                            nutrition_list[i]['quantity'] = str(self.recipe_ingredients[0].sum_nutrient(
                                nutrition_list[i]['quantity'], nutrient['quantity']
                            ))
        return nutrition_list

    @property
    def recipe_ingredients(self):
        """ Proxy property for consistency with Schema.org's standard """
        return self.recipeingredient_set.all()
