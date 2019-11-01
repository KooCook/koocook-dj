from django.shortcuts import render, reverse, redirect, get_list_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .forms import RecipeForm
from ..models import Recipe, RecipeAuthor

from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView


@require_http_methods(["GET"])
# Create your views here.
def index(request):
    return render(request, 'index.html')


@require_http_methods(["GET"])
def search_view(request):
    return render(request, 'search.html')


@require_http_methods(["GET", "DELETE"])
def handle_recipe(request, recipe_id):
    if request.method == 'DELETE':
        Recipe.objects.get(pk=recipe_id).delete()
    return JsonResponse({'status': 'deleted'})


class UserRecipeListView(ListView):
    model = Recipe
    template_name = 'recipes/user.html'
    context_object_name = "user_recipes"

    def get_queryset(self):
        queryset = super().get_queryset()
        author = RecipeAuthor.objects.get(user=self.request.user)
        return get_list_or_404(Recipe, author=author)


class RecipeCreateView(CreateView):
    http_method_names = ['post', 'get']
    form_class = RecipeForm  # model = Recipe
    # fields = '__all__'
    template_name = 'recipes/form.html'

    @property
    def initial(self):
        initial = super().initial
        initial.update({'author': RecipeAuthor.objects.filter(user=self.request.user)[0]})
        return initial.copy()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_success_url(self):
        return reverse('koocook_core:recipe-create')


def detail_view(request):
    return render(request, 'detail.html')
