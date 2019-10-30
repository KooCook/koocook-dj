from django.contrib.auth.models import User
from django.db import models


class Rating(models.Model):
    author = models.OneToOneField(User, on_delete=models.PROTECT)


class Review(models.Model):
    rating_value = models.IntegerField()
    review_body = models.TextField()

    @property
    def item_reviewed(self):
        return
