from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres import fields
from koocook_core.models.base import SerialisableModel


# Create your models here.

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
    avatar = fields.JSONField(default=dict)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferences = fields.JSONField(default=_default_preferences)
    user_settings = fields.JSONField(default=_default_preferences)
    following = models.ManyToManyField('self')
    followers = models.ManyToManyField('self')

    class Meta:
        db_table = 'koocook_auth_user'
        default_related_name = 'koocook_user'

    @property
    def formal_preferences(self):
        from koocook_core.support import PreferenceManager
        return PreferenceManager.from_koocook_user(self)

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

    @property
    def avatar_url(self):
        return self.avatar['content']
