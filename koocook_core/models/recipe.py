from django.contrib.postgres import fields
from django.db import models
from django.http import HttpRequest

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
        blank=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # if not hasattr(self, 'aggregate_rating'):
        #     self.aggregate_rating = create_empty_aggregate_rating()

    @property
    def view_count(self) -> int:
        """
        Returns:
            (int) A view count of the recipe
        """
        return self.recipevisit_set.count()

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


def get_client_ip(request: HttpRequest):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')


class RecipeVisit(models.Model):
    """Represents the visit count of a Recipe

       It is uniquely identified by ip_address, recipe, or user
    """
    class Meta:
        db_table = 'koocook_core_recipe_visit'
        verbose_name = 'Recipe visit count'
        unique_together = (('ip_address', 'recipe'), ('user', 'recipe'))
    ip_address = models.CharField(max_length=45)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey('koocook_core.KoocookUser', on_delete=models.SET_NULL, null=True)
    date_first_visited = models.DateTimeField(auto_now_add=True)
    date_last_visited = models.DateTimeField(auto_now=True)

    @classmethod
    def associate_recipe_with_user(cls, user: 'koocook_core.KoocookUser', recipe: Recipe):
        visit, created = cls.objects.get_or_create(user=user, recipe=recipe)
        return visit

    def add_ip_address(self, request: HttpRequest):
        ip_address = get_client_ip(request)
        try:
            RecipeVisit.objects.filter(ip_address=ip_address)
        except RecipeVisit.DoesNotExist:
            self.ip_address = ip_address


    @classmethod
    def associate_recipe_with_ip_address(cls, request: HttpRequest, recipe: Recipe):
        visit = cls()
        visit.recipe = recipe
        visit.add_ip_address(request)
        return visit

