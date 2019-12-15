import logging
from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseNotAllowed
from django.views.decorators.http import require_http_methods
from django.views.static import serve
from django.conf import settings
from django.urls import re_path

from ..models import Recipe, KoocookUser, Tag, MetaIngredient, RecipeEquipment, Author
from ..models.base import ModelEncoder
from .recipes import RecipeDetailView
# from .decorators import allow_post_comments

LOGGER = logging.getLogger(__name__)


@require_http_methods(["GET"])
def index(request):
    return render(request, 'index.html')


def handle_404(request, exception=None, template_name='base/errors/404.html'):
    return render(request, template_name, status=404)


def handle_500(request, template_name='base/errors/500.html'):
    return render(request, template_name, status=500)


def serve_static() -> list:
    if len(settings.STATICFILES_DIRS) > 0:
        settings_path = settings.STATICFILES_DIRS[0]
    else:
        settings_path = settings.STATIC_ROOT
    return [re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings_path })]


@require_http_methods(["GET", "POST", "DELETE"])
def handle_recipe(request, recipe_id):
    if request.method == 'DELETE' and request.user.is_authenticated:
        recipe = Recipe.objects.get(pk=recipe_id)
        if recipe.author.user == KoocookUser.objects.get(user=request.user):
            recipe_id = recipe.id
            recipe.delete()
            LOGGER.info(f"{recipe.author.user.name} has deleted their recipe named {recipe.name} [{recipe_id}]")
            return JsonResponse({'status': 'deleted'})
        else:
            return HttpResponseForbidden()
    elif request.method == 'GET' or request.method == 'POST':
        response = RecipeDetailView.as_view()
        return response(request, pk=recipe_id)
    else:
        return HttpResponseNotAllowed(["GET", "POST", "DELETE"])


@require_http_methods(["GET"])
def recipe_tags(request):
    name = request.GET.get("name")
    if request.user.is_authenticated:
        LOGGER.info(f"{request.user.username} has requested for all existing recipe tags")
    else:
        LOGGER.info("An anonymous user has requested for all existing recipe tags")
    tags = list(Tag.objects.filter(name__icontains=name))
    return JsonResponse({'current': tags}, encoder=ModelEncoder)


@require_http_methods(["GET"])
def recipe_ingredients(request):
    name = request.GET.get("name")
    ing = list(map(lambda x: x.name, MetaIngredient.objects.filter(name__icontains=name)))
    return JsonResponse({'current': ing}, encoder=ModelEncoder)


@require_http_methods(["GET"])
def recipe_equipment(request):
    name = request.GET.get("name")
    e = list(map(lambda x: x.name, RecipeEquipment.objects.filter(name__icontains=name)))
    return JsonResponse({'current': e}, encoder=ModelEncoder)


@require_http_methods(["GET"])
def recipe_authors(request):
    name = request.GET.get("name")
    e = list(map(lambda x: x.name, Author.objects.filter(name__icontains=name)))
    return JsonResponse({'current': e}, encoder=ModelEncoder)
