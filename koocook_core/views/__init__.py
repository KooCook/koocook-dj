from django.shortcuts import render
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .posts import *
from .recipes import *
from .forms import RecipeForm
from ..models import Recipe, Author
from ..models.user import KoocookUser


@receiver(post_save, sender=User)
def dispatch(sender, instance: User, created, **kwargs):
    if created:
        kc_user = KoocookUser(user=instance)
        kc_user.save()
        author = Author(name=kc_user.name, user=kc_user)
        author.save()


@require_http_methods(["GET"])
def index(request):
    return render(request, 'index.html')


@require_http_methods(["GET", "DELETE"])
def handle_recipe(request, recipe_id):
    if request.method == 'DELETE':
        recipe = Recipe.objects.get(pk=recipe_id)
        if recipe.author.user == KoocookUser.objects.get(user=request.user):
            recipe.delete()
            return JsonResponse({'status': 'deleted'})
        else:
            return HttpResponseForbidden()
    else:
        return HttpResponseForbidden()


def detail_view(request):
    return render(request, 'detail.html')
