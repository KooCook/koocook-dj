from typing import Union

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from ..support import FormattedField
from .base import SerialisableModel

__all__ = ('AggregateRating', 'Comment', 'Rating', 'ReviewableModel')


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


class Comment(SerialisableModel, ReviewableModel, models.Model):
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

    @property
    def item_reviewed(self):
        return self.reviewed_recipe or self.reviewed_post or self.reviewed_comment

    @item_reviewed.setter
    def item_reviewed(self, obj):
        from koocook_core.models.recipe import Recipe
        from koocook_core.models.post import Post
        try:
            if self.reviewed_recipe:
                assert isinstance(obj, Recipe)
                self.reviewed_recipe = obj
            elif self.reviewed_post:
                assert isinstance(obj, Post)
                self.reviewed_post = obj
            elif self.reviewed_comment:
                assert isinstance(obj, self.__class__)
                self.reviewed_comment = obj
        except AssertionError as e:
            raise TypeError('item_reviewed must be of the correct type '
                            '\'{}\' not \'\''.format(
                             type(self.reviewed_recipe or self.reviewed_post or self.reviewed_comment),
                             type(obj))) from e.__context__

    @classmethod
    def field_names(cls):
        return [f.name for f in cls._meta.fields]

    @property
    def rendered(self):
        if hasattr(self.body, 'rendered'):
            return self.body.rendered
        else:
            return self.body


class Rating(models.Model):
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

    @property
    def item_reviewed(self):
        return self.reviewed_recipe or self.reviewed_post or self.reviewed_comment

    @item_reviewed.setter
    def item_reviewed(self, obj):
        from koocook_core.models.recipe import Recipe
        from koocook_core.models.post import Post
        try:
            if self.reviewed_recipe:
                assert isinstance(obj, Recipe)
                self.reviewed_recipe = obj
            elif self.reviewed_post:
                assert isinstance(obj, Post)
                self.reviewed_post = obj
            elif self.reviewed_comment:
                assert isinstance(obj, Comment)
                self.reviewed_comment = obj
        except AssertionError as e:
            raise TypeError('item_reviewed must be of the correct type '
                            '\'{}\' not \'\''.format(
                             type(self.reviewed_recipe or self.reviewed_post or self.reviewed_comment),
                             type(obj))) from e.__context__


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
            raise ValidationError(_('Incompatible bestRating: \'{}\' != \'\''
                                    .format(rating.best_rating, self.best_rating)))
        if rating.worst_rating != self.worst_rating:
            raise ValidationError(_('Incompatible worstRating: \'{}\' != \'\''
                                    .format(rating.worst_rating, self.worst_rating)))
        if rating.item_reviewed != self.item_reviewed:
            raise ValidationError(_('Incompatible itemReviewed: \'{}\' != \'\''
                                    .format(rating.item_reviewed, self.item_reviewed)))

    def add_rating(self, rating: Rating, update=False):
        """Adds a rating from an aggregate rating.

        Raises:
            ValidationError: When `rating` is not valid
        """
        self.check_rating(rating)
        total_value = self.rating_value * self.rating_count
        total_value += rating.rating_value
        if not update:
            self.rating_count += 1
        else:
            total_value -= rating.old_rating_value
        self.rating_value = total_value / self.rating_count
        self.save()

    def remove_rating(self, rating: Rating):
        """Removes a rating from an aggregate rating.

        Raises:
            ValidationError: When `rating` is not valid
        """
        self.check_rating(rating)
        total_value = self.rating_value * self.rating_count
        total_value -= rating.rating_value
        self.rating_count -= 1
        self.rating_value = total_value / self.rating_count
        self.save()

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
