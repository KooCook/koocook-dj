import json
import django
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import reverse
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import RecipeForm
from .mixins import AuthAuthorMixin, CommentWidgetMixin, RecipeViewMixin, SignInRequiredMixin
from ..models import Recipe, Author, KoocookUser, RecipeIngredient, MetaIngredient
from ..models.base import ModelEncoder


class RecipeSearchListView(ListView):
    http_method_names = ('get',)
    model = Recipe
    paginate_by = 10
    context_object_name = 'recipes'
    template_name = 'search.html'

    def get_queryset(self):
        kw = self.request.GET.get("kw")
        if kw:
            return self.model.objects.filter(name__icontains=kw)
        else:
            return self.model.objects.all()


class UserRecipeListView(SignInRequiredMixin, ListView):
    model = Recipe
    template_name = 'recipes/user.html'
    context_object_name = "user_recipes"

    def get_queryset(self):
        queryset = super().get_queryset()
        try:
            author = Author.objects.get(user__user=self.request.user)
        except ObjectDoesNotExist:
            author = Author(user=KoocookUser.objects.get(user=self.request.user))
            author.save()
        return Recipe.objects.filter(author=author)


class RecipeCreateView(AuthAuthorMixin, RecipeViewMixin, CreateView):
    http_method_names = ['post', 'get']
    form_class = RecipeForm  # model = Recipe
    # fields = '__all__'
    template_name = 'recipes/create.html'

    @property
    def initial(self):
        initial = super().initial
        initial.update({'aggregate_rating_id': 1})
        initial.update({'author': Author.objects.filter(user__user=self.request.user)[0]})
        return initial.copy()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_success_url(self):
        return reverse('koocook_core:recipe-user')


class RecipeUpdateView(AuthAuthorMixin, RecipeViewMixin, UpdateView):
    model = Recipe
    fields = '__all__'  # ['name']
    template_name = 'recipes/update.html'

    def get_success_url(self):
        return reverse('koocook_core:recipe-user')

    def get_context_data(self, **kwargs):
        import json
        context = super().get_context_data(**kwargs)
        context['ingredients'] = json.dumps([ing.to_dict for ing in list(self.get_object().recipe_ingredients.all())])
        context['tags'] = json.dumps([ing.as_dict for ing in list(self.get_object().tag_set.all())], cls=ModelEncoder)
        return context


class RecipeDetailView(CommentWidgetMixin, DetailView):
    model = Recipe
    template_name = 'recipes/detail.html'

    def get_success_url(self):
        return self.request.path

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ingredients'] = [ing.to_dict for ing in list(self.get_object().recipe_ingredients.all())]
        return context
