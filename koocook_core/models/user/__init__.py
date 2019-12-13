from django.contrib.auth.models import User
from django.contrib.postgres import fields
from django.db import models

from koocook_auth.models import KoocookUser
from ..base import SerialisableModel

__all__ = ['Author', 'KoocookUser']


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
    
    name = models.CharField(max_length=100)
    user = models.OneToOneField(
        'koocook_auth.KoocookUser',
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
