import json
from django.db import models
from django.utils.html import mark_safe

from .base import SerialisableModel
from .review import ReviewableModel
from ..support import FormattedField

__all__ = ('Post',)


class Post(SerialisableModel, ReviewableModel, models.Model):
    include = ('rendered',)
    author = models.ForeignKey(
        'koocook_core.Author',
        on_delete=models.PROTECT,
    )
    date_published = models.DateTimeField(auto_now_add=True)
    body = FormattedField()
    # comment_set from Comment's ForeignKey
    aggregate_rating = models.OneToOneField(
        'koocook_core.AggregateRating',
        on_delete=models.PROTECT,
        blank=True,
        # default=create_empty_aggregate_rating,
    )

    @property
    def rendered(self):
        if hasattr(self.body, 'rendered'):
            return self.body.rendered
        else:
            return self.body
