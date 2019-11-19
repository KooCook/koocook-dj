from django.contrib.auth.models import User
from django.contrib.postgres import fields
from django.db import models

from .base import SerialisableModel

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
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferences = fields.JSONField(default=_default_preferences)
    user_settings = fields.JSONField(default=_default_preferences)
    following = models.ManyToManyField('self')
    followers = models.ManyToManyField('self')

    class Meta:
        db_table = 'koocook_core_koocookuser'

    def follow(self, user: 'KoocookUser'):
        pass

    def unfollow(self, user: 'KoocookUser'):
        pass

    @property
    def name(self):
        if self.user.get_full_name():
            return self.user.get_full_name()
        else:
            return self.user.username

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
    name = models.CharField(max_length=100)
    koocook_user = models.OneToOneField(
        'koocook_core.KoocookUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            assert 'koocook_user' not in kwargs, "don't user 'user' with 'koocook_user'!"
            kwargs['koocook_user'] = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    @property
    def dj_user(self):
        return self.koocook_user.user

    @classmethod
    def from_dj_user(cls, user: User):
        return cls.objects.get(koocook_user__user=user)

    @property
    def qualified_name(self):
        if self.koocook_user and self.koocook_user.full_name:
            return self.koocook_user.full_name
        else:
            return self.name

    @property
    def as_dict(self):
        base_dict_repr = super().as_dict
        base_dict_repr.update({'qualified_name': self.qualified_name})
        return base_dict_repr

    def __str__(self):
        return self.qualified_name
