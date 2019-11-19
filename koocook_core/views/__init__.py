from django.shortcuts import render, reverse, redirect, get_object_or_404
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
    return render(request, 'index.html', {'object': Recipe.objects.all()})


@require_http_methods(["GET"])
def search_view(request):
    return render(request, 'search.html')


@require_http_methods(["GET", "DELETE"])
def handle_recipe(request, recipe_id):
    if request.method == 'DELETE':
        recipe = Recipe.objects.get(pk=recipe_id)
        if recipe.author.user == KoocookUser.objects.get(user=request.user):
            recipe.delete()
            return JsonResponse({'status': 'deleted'})
        else:
            return HttpResponseForbidden()
    elif request.method == 'GET':
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        response = RecipeDetailView.as_view()
        return response(request, pk=recipe_id)
    else:
        return HttpResponseForbidden()
