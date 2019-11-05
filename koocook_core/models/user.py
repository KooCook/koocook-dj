from django.contrib.auth.models import User
from django.contrib.postgres import fields
from django.db import models

__all__ = ['KoocookUser', 'Author']


def _default_preferences():
    return dict()


class KoocookUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # author from Author's OneToOneField
    preferences = fields.JSONField(default=_default_preferences)
    user_settings = fields.JSONField(default=_default_preferences)
    following = models.ManyToManyField('self')
    followers = models.ManyToManyField('self')

    def follow(self, user: 'KoocookUser'):
        pass

    def unfollow(self, user: 'KoocookUser'):
        pass


class Author(models.Model):
    name = models.CharField(max_length=63)
    user = models.OneToOneField(
        'koocook_core.KoocookUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    # rating_set from Rating
    # comment_set from Comment
    # recipe_set from Recipe
    # post_set from Post

    def __str__(self):
        return self.name
