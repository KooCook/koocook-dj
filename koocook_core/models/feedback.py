from django.db import models
from django.contrib.postgres import fields

__all__ = ('Feedback',)


class Feedback(models.Model):
    author = models.ForeignKey(
        'koocook_core.Author',
        on_delete=models.PROTECT,
        null=True
    )
    date_published = models.DateTimeField(auto_now_add=True)
    subject = models.CharField(max_length=100)
    body = models.TextField()
    image = fields.ArrayField(models.CharField(max_length=200), null=True, blank=True)
    video = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.subject
