from django.shortcuts import render, get_object_or_404
from .models.recipe import Recipe


# Create your views here.
def index(request):
    return render(request, 'index.html')


def search_view(request):
    return render(request, 'search.html')


def detail_view(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    return render(request, 'detail.html', {'recipe': recipe})
