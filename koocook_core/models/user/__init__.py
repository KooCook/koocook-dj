from django.contrib.auth.models import User
from django.contrib.postgres import fields
from django.db import models

from ..base import SerialisableModel

__all__ = ['Author', 'KoocookUser']


def _default_preferences():
    return dict()


class KoocookUser(SerialisableModel, models.Model):
    """

    Attributes:
        author (Author): from OneToOneField in ``Author``

    Notes:
        Automatically created when ``User`` is  created.
    """
    exclude = ('user', 'preferences', 'user_settings')

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferences = fields.JSONField(default=_default_preferences)
    user_settings = fields.JSONField(default=_default_preferences)
    following = models.ManyToManyField('self')
    followers = models.ManyToManyField('self')

    class Meta:
        db_table = 'koocook_core_koocook_user'

    def follow(self, user: 'KoocookUser'):
        self.following.add(user)
        user.followers.add(self)

    def unfollow(self, user: 'KoocookUser'):
        self.following.remove(user)
        user.followers.remove(self)
        self.save()

    @property
    def name(self):
        if self.user.get_full_name():
            return self.user.get_full_name()
        else:
            return self.user.username

    @classmethod
    def from_dj_user(cls, user: User):
        return cls.objects.get(user=user)

    @property
    def full_name(self):
        return self.user.get_full_name()


class Author(SerialisableModel, models.Model):
    """

    Attributes:
        rating_set (RelatedManager): from ForeignKey in ``Rating``
        comment_set (RelatedManager): from ForeignKey in ``Comment``
        recipe_set (RelatedManager): from ForeignKey in ``Recipe``
        post_set (RelatedManager): from ForeignKey in ``Post``

    Notes:
        Automatically created when ``User`` is  created.
    """
    include = ('qualified_name',)
    exclude = ()

    name = models.CharField(max_length=100)
    user = models.OneToOneField(
        'koocook_core.KoocookUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    @property
    def dj_user(self):
        return self.user.user

    @classmethod
    def from_dj_user(cls, user: User):
        return cls.objects.get(user__user=user)

    @property
    def qualified_name(self):
        if self.user and self.user.full_name:
            return self.user.full_name
        else:
            return self.name

    @property
    def as_dict(self):
        base_dict_repr = super().as_dict
        base_dict_repr.update({'qualified_name': self.qualified_name})
        return base_dict_repr

    def __str__(self):
        return self.qualified_name
