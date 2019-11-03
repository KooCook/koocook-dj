from django.shortcuts import render, reverse, redirect, get_list_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from .forms import RecipeForm
from ..models import Recipe, RecipeAuthor

from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView


@require_http_methods(["GET"])
def index(request):
    return render(request, 'index.html')


@require_http_methods(["GET"])
def search_view(request):
    return render(request, 'search.html')


@require_http_methods(["GET", "DELETE"])
def handle_recipe(request, recipe_id):
    if request.method == 'DELETE':
        recipe = Recipe.objects.get(pk=recipe_id)
        if recipe.author.user == request.user:
            recipe.delete()
            return JsonResponse({'status': 'deleted'})
        else:
            return HttpResponseForbidden()
    else:
        return HttpResponseForbidden()


class UserRecipeListView(ListView):
    model = Recipe
    template_name = 'recipes/user.html'
    context_object_name = "user_recipes"

    def get_queryset(self):
        queryset = super().get_queryset()
        author = RecipeAuthor.objects.get(user=self.request.user)
        return Recipe.objects.filter(author=author)


class RecipeCreateView(CreateView):
    http_method_names = ['post', 'get']
    form_class = RecipeForm  # model = Recipe
    # fields = '__all__'
    template_name = 'recipes/create.html'

    @property
    def initial(self):
        initial = super().initial
        initial.update({'author': RecipeAuthor.objects.filter(user=self.request.user)[0]})
        return initial.copy()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_success_url(self):
        return reverse('koocook_core:recipe-user')


class RecipeUpdateView(UpdateView):
    model = Recipe
    fields = ['name']
    template_name = 'recipes/update.html'

    def get_success_url(self):
        return reverse('koocook_core:recipe-user')


def detail_view(request):
    return render(request, 'detail.html')
