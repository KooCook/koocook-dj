from typing import Union, Any, Dict
from decimal import Decimal

from django.db import models
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from .base import SerialisableModel

from ..support import FormattedField
from .base import SerialisableModel

__all__ = ['AggregateRating', 'Rating', 'Comment']


def _add_rating(old_value: Decimal, old_count: int,
                new_rating: Union[int, float]) -> Decimal:
    old_total = old_value * old_count
    return (old_total + round(Decimal(new_rating), 1)) / (old_count + 1)


def _remove_rating(old_value: Decimal, old_count: int,
                   new_rating: Union[int, float]) -> Decimal:
    old_total = old_value * old_count
    return (old_total - round(Decimal(new_rating), 1)) / (old_count - 1)


class AggregateRating(models.Model):
    """

    Notes:
        attribute 'recipe' from Recipe's OneToOneField
        attribute 'post' from Post's OneToOneField
        attribute 'comment' from Comment's OneToOneField
    """
    rating_value = models.DecimalField(
        decimal_places=10,
        max_digits=13,
        # every vote counts until 10 B
    )
    rating_count = models.IntegerField()
    best_rating = models.IntegerField(default=5)
    worst_rating = models.IntegerField(default=1)

    def check_rating(self, rating: 'Rating') -> None:
        """Checks if rating is of the same type and origin or not.

        Raises:
            ValidationError: When `rating` is not valid
        """
        if rating.item_reviewed != self.item_reviewed:
            raise ValidationError(
                _(f'incompatible item_reviewed: '
                  f"'{rating.item_reviewed}' != '{self.item_reviewed}'"))
        if rating.best_rating != self.best_rating:
            raise ValidationError(
                _(f'incompatible best_rating: '
                  f"'{rating.best_rating}' != '{self.best_rating}'"))
        if rating.worst_rating != self.worst_rating:
            raise ValidationError(
                _(f'incompatible worst_rating: '
                  f"'{rating.worst_rating}' != '{self.worst_rating}'"))

    def add_rating(self, rating: 'Rating'):
        """Adds a rating from an aggregate rating.

        Raises:
            ValidationError: When `rating` is not valid
        """
        self.check_rating(rating)
        if rating.used:
            raise ValidationError(
                _("rating is already tabulated somewhere, can't add"))
        self.rating_value = _add_rating(self.rating_value, self.rating_count,
                                        rating.rating_value)
        self.rating_count += 1
        self.save()
        assert not rating.used, "rating shouldn't have been used yet"
        rating.used = True
        rating.save()

    def remove_rating(self, rating: 'Rating'):
        """Removes a rating from an aggregate rating.

        Raises:
            ValidationError: When `rating` is not valid
        """
        self.check_rating(rating)
        if not rating.used:
            raise ValidationError(
                _("rating is not tabulated yet, can't remove"))
        self.rating_value = _remove_rating(self.rating_value,
                                           self.rating_count,
                                           rating.rating_value)
        self.rating_count -= 1
        self.save()
        assert rating.used, "rating should have been used"
        rating.used = False
        rating.save()

    @property
    def item_reviewed(self) -> Union['Recipe', 'Post', 'Comment', None]:
        try:
            return self.recipe
        except ObjectDoesNotExist:
            pass
        try:
            return self.post
        except ObjectDoesNotExist:
            pass
        try:
            return self.comment
        except ObjectDoesNotExist:
            pass

    @classmethod
    def create_empty(cls, **kwargs) -> 'AggregateRating':
        """Creates a new empty ``aggregate rating``."""
        kwargs['rating_value'] = kwargs.pop('rating_value', 0)
        kwargs['rating_count'] = kwargs.pop('rating_count', 0)
        return cls.objects.create(**kwargs)


def create_empty_aggregate_rating(**kwargs) -> 'AggregateRating':
    """Creates an empty aggregate rating"""
    return AggregateRating.objects.create(rating_value=0, rating_count=0, **kwargs)


class Comment(SerialisableModel, models.Model):
    exclude = ('reviewed_comment', 'reviewed_recipe', 'reviewed_post')
    author = models.ForeignKey(
        'koocook_core.Author',
        on_delete=models.PROTECT,
    )
    date_published = models.DateTimeField(auto_now_add=True)
    body = FormattedField()  # models.TextField()
    aggregate_rating = models.OneToOneField(
        'koocook_core.AggregateRating',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        default=AggregateRating.create_empty,
    )
    reviewed_recipe = models.ForeignKey(
        'koocook_core.Recipe',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    reviewed_post = models.ForeignKey(
        'koocook_core.Post',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    reviewed_comment = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    def __init__(self, *args, **kwargs):
        kwargs = parse_kwargs_item_reviewed(kwargs)
        super().__init__(*args, **kwargs)

    @property
    def item_reviewed(self) -> Union['Recipe', 'Post', 'Comment', None]:
        return self.reviewed_recipe or self.reviewed_post or self.reviewed_comment

    @classmethod
    def field_names(cls):
        return [f.name for f in cls._meta.fields]

    @property
    def processed_body(self):
        if hasattr(self.body, 'rendered'):
            return self.body.rendered
        else:
            return self.body

    @property
    def as_dict(self):
        base_dict_repr = super().as_dict
        base_dict_repr.update({'rendered': self.processed_body})
        return base_dict_repr


class Rating(models.Model):
    author = models.ForeignKey(
        'koocook_core.Author',
        on_delete=models.PROTECT,
    )
    rating_value = models.IntegerField()
    best_rating = models.IntegerField(default=5)
    worst_rating = models.IntegerField(default=1)
    reviewed_recipe = models.ForeignKey(
        'koocook_core.Recipe',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    reviewed_post = models.ForeignKey(
        'koocook_core.Post',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    reviewed_comment = models.ForeignKey(
        'koocook_core.Comment',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    used = models.BooleanField(default=False, blank=True)

    def __init__(self, *args, **kwargs):
        kwargs = parse_kwargs_item_reviewed(kwargs)
        if not kwargs.get('worst_rating', 1) <= \
               kwargs['rating_value'] <= \
               kwargs.get('best_rating', 5):
            raise ValueError('`rating_value` must be between `best_rating` and '
                             '`worst_rating`')
        super().__init__(*args, **kwargs)

    @property
    def item_reviewed(self) -> Union['Recipe', 'Post', 'Comment', None]:
        return self.reviewed_recipe or self.reviewed_post or self.reviewed_comment


def parse_kwargs_item_reviewed(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    item = kwargs.pop('item_reviewed', None)
    if item:
        assert not any(
            k in kwargs
            for k in ('reviewed_recipe', 'reviewed_post', 'reviewed_comment')
        ), "Don't specify both item reviewed and the actual item reviewed"
        from koocook_core.models.recipe import Recipe
        from koocook_core.models.post import Post
        if isinstance(item, Recipe):
            kwargs['reviewed_recipe'] = item
        elif isinstance(item, Post):
            kwargs['reviewed_post'] = item
        elif isinstance(item, Comment):
            kwargs['reviewed_comment'] = item
        else:
            raise TypeError(f'item_reviewed must be of the type Recipe, '
                            f"Post or Comment not '{type(item)}'")
    else:
        # monkey patch
        if kwargs == {}:
            return {}
        count = list(k in kwargs for k in ('reviewed_recipe', 'reviewed_post',
                                           'reviewed_comment')).count(True)
        if count != 1:
            raise ValueError(f'There must be 1 reviewed item, not {count}')
    return kwargs
