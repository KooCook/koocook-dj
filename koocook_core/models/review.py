from typing import Union, Dict, Any
from decimal import Decimal, DivisionByZero

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from ..support import FormattedField
from .base import SerialisableModel

__all__ = ('AggregateRating', 'Comment', 'Rating', 'ReviewableModel')


def _add_rating(old_value: Decimal, old_count: int,
                new_rating: Union[int, float]) -> Decimal:
    old_total = old_value * old_count
    try:
        return (old_total + round(Decimal(new_rating), 1)) / (old_count + 1)
    except DivisionByZero:
        return old_total + round(Decimal(new_rating), 1)


def _remove_rating(old_value: Decimal, old_count: int,
                   new_rating: Union[int, float]) -> Decimal:
    old_total = old_value * old_count
    try:
        return (old_total - round(Decimal(new_rating), 1)) / (old_count - 1)
    except DivisionByZero:
        return old_total - round(Decimal(new_rating), 1)


class ReviewerModel:
    """Mixin for models that can review ReviewableModels"""
    @property
    def item_reviewed(self):
        return self.reviewed_recipe or self.reviewed_post or self.reviewed_comment

    @item_reviewed.setter
    def item_reviewed(self, value):
        kwarg = parse_kwargs_item_reviewed({'item_reviewed': value})
        count = 0
        for k, v in kwarg.items():
            setattr(self, k, v)
            count += 1
            if count > 1:
                raise AssertionError


class ReviewableModel:
    """This creates an AggregateRating only after reviewables are actually created
    and saved to a database; that is, it will be created once in need, not always.
    """
    aggregate_rating = None  # A signature for the AggregateRating field

    def save(self, *args, **kwargs):
        # If the aggregate rating of a reviewable has not yet been created
        try:
            rating = getattr(self, 'aggregate_rating')
            if not rating:
                self.aggregate_rating = AggregateRating.create_empty()
        except AggregateRating.DoesNotExist:
            self.aggregate_rating = AggregateRating.create_empty()
        super().save(*args, **kwargs)  # Resolved at runtime


class Comment(ReviewerModel, SerialisableModel, ReviewableModel, models.Model):
    include = ("rendered",)
    exclude = ('reviewed_comment', 'reviewed_recipe', 'reviewed_post')
    author = models.ForeignKey(
        'koocook_core.Author',
        on_delete=models.PROTECT,
    )
    date_published = models.DateTimeField(auto_now_add=True)
    body = FormattedField()  # models.TextField()
    aggregate_rating = models.OneToOneField(
        'koocook_core.AggregateRating',
        on_delete=models.PROTECT, blank=True, null=True
    )
    # item_reviewed = models.URLField()
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
        kwargs = parse_kwargs_item_reviewed(kwargs, strict=False)
        super().__init__(*args, **kwargs)

    @classmethod
    def field_names(cls):
        return [f.name for f in cls._meta.fields]

    @property
    def rendered(self):
        if hasattr(self.body, 'rendered'):
            return self.body.rendered
        else:
            return self.body

    def save(self, *args, **kwargs):
        if self.item_reviewed is None:
            raise ValidationError(_('There must be at least 1 item reviewed'))
        super().save(*args, **kwargs)


class Rating(ReviewerModel, models.Model):
    author = models.ForeignKey(
        'koocook_core.Author',
        on_delete=models.PROTECT,
    )
    rating_value = models.IntegerField()
    best_rating = models.IntegerField(default=5)
    worst_rating = models.IntegerField(default=1)
    # item_reviewed = models.URLField()
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
        kwargs = parse_kwargs_item_reviewed(kwargs, strict=False)
        if 'rating_value' in kwargs:
            if not kwargs.get('worst_rating', 1) <= \
                   kwargs['rating_value'] <= \
                   kwargs.get('best_rating', 5):
                raise ValueError('`rating_value` must be between `best_rating` and '
                                 '`worst_rating`')
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        if self.item_reviewed is None:
            raise ValidationError(_('There must be at least 1 item reviewed'))
        super().save(*args, **kwargs)


def parse_kwargs_item_reviewed(kwargs: Dict[str, Any], strict: bool = True) -> Dict[str, Any]:
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
        count = list(k in kwargs for k in ('reviewed_recipe', 'reviewed_post',
                                           'reviewed_comment')).count(True)
        if count != 1:
            if strict:
                raise ValueError(f'There must be 1 reviewed item, not {count}')
            return kwargs
    return kwargs


class AggregateRating(models.Model):
    rating_value = models.DecimalField(
        decimal_places=10,
        max_digits=13,
        # every vote counts until 10 B
    )
    rating_count = models.IntegerField()
    best_rating = models.IntegerField(default=5)
    worst_rating = models.IntegerField(default=1)
    # recipe from Recipe's OneToOneField
    # post from Post's OneToOneField
    # comment from Comment's OneToOneField

    def check_rating(self, rating: Rating) -> None:
        """Checks if rating is of the same type and origin or not.

        Raises:
            ValidationError: When `rating` is not valid
        """
        if rating.best_rating != self.best_rating:
            raise ValidationError(_('Incompatible bestRating: \'{}\' != \'{}\''
                                    .format(rating.best_rating, self.best_rating)))
        if rating.worst_rating != self.worst_rating:
            raise ValidationError(_('Incompatible worstRating: \'{}\' != \'{}\''
                                    .format(rating.worst_rating, self.worst_rating)))
        if rating.item_reviewed != self.item_reviewed:
            raise ValidationError(_('Incompatible itemReviewed: \'{}\' != \'{}\''
                                    .format(rating.item_reviewed, self.item_reviewed)))

    def add_rating(self, rating: Rating, update=False):
        """Adds a rating from an aggregate rating.

        Raises:
            ValidationError: When `rating` is not valid
        """
        self.check_rating(rating)
        if update:
            self.remove_rating(rating)
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

    def remove_rating(self, rating: Rating):
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
        kwargs['rating_value'] = 0 # kwargs.pop('rating_value', 0)
        kwargs['rating_count'] = 0 # kwargs.pop('rating_count', 0)
        return cls.objects.create(**kwargs)

    def __str__(self) -> str:
        return str(self.rating_value)

    def __le__(self, other) -> bool:
        return self.rating_value <= other.rating_value

    def __eq__(self, other) -> bool:
        return self.rating_value == other.rating_value

    def __lt__(self, other) -> bool:
        return self.rating_value < other.rating_value

    def __ge__(self, other) -> bool:
        return self.rating_value >= other.rating_value

    def __gt__(self, other) -> bool:
        return self.rating_value > other.rating_value
