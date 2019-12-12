from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .comments import *
from .posts import *
from .recipes import *
from .handlers import *
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
