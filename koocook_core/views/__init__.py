from django.shortcuts import render, reverse
from django.views.decorators.http import require_http_methods
from .models import Recipe
from django import forms
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView


class RecipeForm(forms.ModelForm):
    customised_field = ['name']

    class Meta:
        model = Recipe
        fields = '__all__'

    @property
    def vanilla_fields(self):
        return [field for field in self if not (field.name in self.customised_field or field.is_hidden)]


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

    def get_success_url(self):
        return reverse('koocook_core:recipe-create')


def detail_view(request):
    return render(request, 'detail.html')
