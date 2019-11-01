from django.shortcuts import render, reverse, redirect
from django.views.decorators.http import require_http_methods
from .forms import RecipeForm
from ..models import RecipeAuthor

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

    def get_success_url(self):
        return reverse('koocook_core:recipe-create')


def detail_view(request):
    return render(request, 'detail.html')
