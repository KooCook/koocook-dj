import logging
from django.contrib.postgres import fields
from django.db import models
from django.http import HttpRequest

from koocook_core import fields as koocookfields

from .review import ReviewableModel

__all__ = ['Recipe']

LOGGER = logging.getLogger(__name__)


class Recipe(ReviewableModel, models.Model):
    """

    Attributes:
        recipeingredient_set (RelatedManager): from ForeignKey in ``Ingredient``
        comment_set (RelatedManager): from ForeignKey in ``Comment``

    References:
        https://developers.google.com/search/docs/data-types/recipe
        https://schema.org/Recipe
    """
    name = models.CharField(max_length=255)
    image = fields.ArrayField(
        models.CharField(max_length=200),
        null=True,
        blank=True,
    )
    video = models.URLField(null=True, blank=True)
    author = models.ForeignKey(
        'koocook_core.Author',
        on_delete=models.PROTECT,
        null=True,
    )
    # Refactor this to use custom save() later https://stackoverflow.com/questions/1737017/django-auto-now-and-auto-now-add
    date_published = models.DateTimeField(
        auto_now_add=True,
        null=True,
    )
    description = models.TextField()
    prep_time = models.DurationField(null=True)
    cook_time = models.DurationField(null=True)
    recipe_instructions = fields.ArrayField(models.TextField(), default=list)
    recipe_yield = koocookfields.QuantityField(null=True)
    tag_set = models.ManyToManyField('koocook_core.Tag', blank=True)
    aggregate_rating = models.OneToOneField(
        'koocook_core.AggregateRating',
        on_delete=models.PROTECT,
        blank=True,
    )

    @property
    def view_count(self) -> int:
        """
        Returns:
            (int) A view count of the recipe
        """
        return self.recipevisit_set.count()

    def update(self, dct: dict, save: bool = True) -> None:
        for field, value in dct.items():
            try:
                setattr(self, field, value)
            except TypeError:
                getattr(self, field).set(value)
        if save:
            self.save()

    @property
    def popularity_score(self) -> float:
        return ((float(self.view_count)*1.9)+(float(self.aggregate_rating.rating_value)*3.1))/5

    @property
    def total_time(self):
        try:
            return self.prep_time + self.cook_time
        except TypeError:
            return

    @property
    def nutrition(self):
        return

    @property
    def recipe_ingredients(self):
        """ Proxy property for consistency with Schema.org's standard """
        return self.recipeingredient_set.all()


def get_client_ip(request: HttpRequest):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')


class RecipeVisit(models.Model):
    """Represents the visit count of a Recipe

       It is uniquely identified by ip_address, recipe, or user.
    """
    class Meta:
        db_table = 'koocook_core_recipe_visit'
        verbose_name = 'Recipe visit count'
        unique_together = (('ip_address', 'user', 'recipe'), ('user', 'recipe'))
    ip_address = models.CharField(max_length=45)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey('koocook_auth.KoocookUser', on_delete=models.SET_NULL, null=True)
    date_first_visited = models.DateTimeField(auto_now_add=True)
    date_last_visited = models.DateTimeField(auto_now=True)

    @classmethod
    def associate_recipe_with_user(cls, user: 'koocook_auth.KoocookUser', recipe: Recipe):
        visit, created = cls.objects.get_or_create(user=user, recipe=recipe)
        LOGGER.info(f"Incoming visit to {recipe.name} [{recipe.id}] from {user.name}")
        return visit

    def add_ip_address(self, request: HttpRequest, recipe: Recipe) -> str:
        ip_address = get_client_ip(request)
        self.first = False
        self.ip_address = ip_address
        return ip_address

    @classmethod
    def associate_recipe_with_ip_address(cls, request: HttpRequest, recipe: Recipe):
        address = get_client_ip(request)
        LOGGER.info(f"Incoming visit to {recipe.name} [{recipe.id}] from {address}")
        visit, created = cls.objects.get_or_create(user=None,
                                                   ip_address=address,
                                                   recipe=recipe)
        visit.save()
        return visit
