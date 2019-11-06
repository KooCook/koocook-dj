import json
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import reverse
from django.views.generic.edit import CreateView, ProcessFormView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView

from .forms import RecipeForm
from ..models import Recipe, Author, KooCookUser, Ingredient, MetaIngredient
from ..support import Quantity


class RecipeViewMixin:
    def form_valid(self, form):
        response = super().form_valid(form)
        ingredients = json.loads(self.request.POST.get('ingredients'))
        if ingredients:
            for ingredient in ingredients:
                meta = MetaIngredient(name=ingredient['name'])
                meta.save()
                Ingredient(meta=meta, recipe=form.save(commit=False),
                           quantity=f"{ingredient['quantity']['number']} {ingredient['quantity']['unit']}").save()
            return response
        else:
            return response


class UserRecipeListView(ListView):
    model = Recipe
    template_name = 'recipes/user.html'
    context_object_name = "user_recipes"

    def get_queryset(self):
        queryset = super().get_queryset()
        try:
            author = Author.objects.get(user__user=self.request.user)
        except ObjectDoesNotExist:
            author = Author(user=KooCookUser.objects.get(user=self.request.user))
            author.save()
        return Recipe.objects.filter(author=author)


class RecipeCreateView(RecipeViewMixin, CreateView):
    http_method_names = ['post', 'get']
    form_class = RecipeForm  # model = Recipe
    # fields = '__all__'
    template_name = 'recipes/create.html'

    @property
    def initial(self):
        initial = super().initial
        initial.update({'author': Author.objects.filter(user__user=self.request.user)[0]})
        return initial.copy()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_success_url(self):
        return reverse('koocook_core:recipe-user')


class RecipeUpdateView(UpdateView):
    model = Recipe
    fields = '__all__'  # ['name']
    template_name = 'recipes/update.html'

    def get_success_url(self):
        return reverse('koocook_core:recipe-user')

    def get_context_data(self, **kwargs):
        import json
        context = super().get_context_data(**kwargs)
        context['ingredients'] = json.dumps([ing.to_dict for ing in list(self.get_object().recipe_ingredients.all())])
        return context
