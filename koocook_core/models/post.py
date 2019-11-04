from django.db import models

__all__ = ['Post']


class Post(models.Model):
    author = models.ForeignKey(
        'koocook_core.Author',
        on_delete=models.PROTECT,
    )
    date_published = models.DateTimeField()
    body = models.TextField
    # comment_set from Comment's ForeignKey
    aggregate_rating = models.OneToOneField(
        'koocook_core.AggregateRating',
        on_delete=models.PROTECT,
    )
