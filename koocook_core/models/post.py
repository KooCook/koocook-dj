import json
from django.db import models
from django.utils.html import mark_safe

from .base import SerialisableModel
from .review import create_empty_aggregate_rating
from ..support import MarkdownField

__all__ = ('Post',)


class Post(SerialisableModel, models.Model):
    author = models.ForeignKey(
        'koocook_core.Author',
        on_delete=models.PROTECT,
    )
    date_published = models.DateTimeField(auto_now_add=True)
    body = MarkdownField()
    # comment_set from Comment's ForeignKey
    aggregate_rating = models.OneToOneField(
        'koocook_core.AggregateRating',
        on_delete=models.PROTECT,
        blank=True,
        default=create_empty_aggregate_rating,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not hasattr(self, 'aggregate_rating'):
            self.aggregate_rating = create_empty_aggregate_rating()

    @property
    def processed_body(self):
        if hasattr(self.body, 'rendered'):
            return self.body.rendered
        else:
            return self.body

    @property
    def as_dict(self):
        base_dict_repr = super().as_dict
        base_dict_repr.update({'renderedBody': self.processed_body})
        return base_dict_repr

