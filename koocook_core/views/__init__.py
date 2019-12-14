
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .comments import *
from .posts import *
from .recipes import *
from .handlers import *
from .ingredients import *
from .forms import RecipeForm
from .profile import UserProfileInfoView, UserSettingsInfoView
from ..models import Author, Recipe
from ..models.user import KoocookUser


@receiver(post_save, sender=User)
def dispatch(sender, instance: User, created, **kwargs):
    if created:
        kc_user = KoocookUser(user=instance)
        kc_user.save()
        author = Author(name=kc_user.name, user=kc_user)
        author.save()

