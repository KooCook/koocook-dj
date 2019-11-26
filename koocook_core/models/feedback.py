from django.db import models
from .base import SerialisableModel

__all__ = ('Feedback',)


class Feedback(models.Model):
    author = models.ForeignKey(
        'koocook_core.Author',
        on_delete=models.PROTECT,
    )
    date_published = models.DateTimeField(auto_now_add=True)
    subject = models.CharField(max_length=100)
    body = models.TextField()
