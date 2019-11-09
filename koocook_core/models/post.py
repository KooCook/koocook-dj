import json
from django.db import models
from django.utils.html import mark_safe

from .base import SerialisableModel

__all__ = ('Post',)


class Post(SerialisableModel, models.Model):
    author = models.ForeignKey(
        'koocook_core.Author',
        on_delete=models.PROTECT,
    )
    date_published = models.DateTimeField(auto_now_add=True)
    body = models.TextField()
    # comment_set from Comment's ForeignKey
    aggregate_rating = models.OneToOneField(
        'koocook_core.AggregateRating', null=True,
        on_delete=models.PROTECT,
    )

    @property
    def processed_body(self):
        return self.process_text_format(self.body)

    @property
    def as_dict(self):
        base_dict_repr = super().as_dict
        base_dict_repr.update({'body': self.processed_body})
        return base_dict_repr

