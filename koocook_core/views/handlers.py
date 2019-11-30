import json
from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from ..models import Recipe, KoocookUser, Tag
from ..models.base import ModelEncoder
from .recipes import RecipeDetailView
from .decorators import allow_post_comments


@require_http_methods(["GET"])
def index(request):
    return render(request, 'index.html')


@require_http_methods(["GET", "POST", "DELETE"])
@allow_post_comments(Recipe, 'recipe_id')
def handle_recipe(request, recipe_id):
    if request.method == 'DELETE' and request.user.is_authenticated:
        recipe = Recipe.objects.get(pk=recipe_id)
        if recipe.author.user == KoocookUser.objects.get(user=request.user):
            recipe.delete()
            return JsonResponse({'status': 'deleted'})
        else:
            return HttpResponseForbidden()
    elif request.method == 'GET' or request.method == 'POST':
        response = RecipeDetailView.as_view()
        return response(request, pk=recipe_id)
    else:
        return HttpResponseForbidden()


@require_http_methods(["GET"])
def recipe_tags(request):
    name = request.GET.get("name")
    tags = list(Tag.objects.filter(name__icontains=name))
    return JsonResponse({'current': tags}, encoder=ModelEncoder)
