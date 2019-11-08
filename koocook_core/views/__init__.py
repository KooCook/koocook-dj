from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .recipes import *
from .handlers import *
from .forms import RecipeForm
from ..models import Author
from ..models.user import KoocookUser


@receiver(post_save, sender=User)
def dispatch(sender, instance: User, created, **kwargs):
    if created:
        kc_user = KoocookUser(user=instance)
        kc_user.save()
        author = Author(name=kc_user.name, user=kc_user)
        author.save()

