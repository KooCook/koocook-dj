import json
import django
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import reverse
from django.views.generic.edit import CreateView, ProcessFormView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import RecipeForm
from ..models import Recipe, Author, KoocookUser, RecipeIngredient, MetaIngredient
from ..support import Quantity


class SignInRequiredMixin(LoginRequiredMixin):
    @property
    def login_url(self):
        return reverse('social:begin', args=['google-oauth2'])


class RecipeViewMixin:
    def form_valid(self, form):
        response = super().form_valid(form)
        ingredients = json.loads(self.request.POST.get('ingredients'))
        if ingredients:
            for ingredient in ingredients:
                meta_queryset = MetaIngredient.objects.filter(name=ingredient['name'])
                if not meta_queryset.exists():
                    meta = MetaIngredient(name=ingredient['name'])
                    meta.save()
                else:
                    meta = meta_queryset[0]
                ingredient_field_values = {'meta': meta, 'recipe': form.save(commit=False),
                                           'quantity': f"{ingredient['quantity']['number']} "
                                                       f"{ingredient['quantity']['unit']}"}
                if 'id' not in ingredient:
                    RecipeIngredient(**ingredient_field_values).save()
                else:
                    found_ingredient = RecipeIngredient.objects.filter(pk=ingredient['id'])
                    if not found_ingredient:
                        RecipeIngredient(**ingredient_field_values).save()
                    else:
                        if 'removed' in ingredient and bool(ingredient['removed']):
                            found_ingredient.delete()
                        else:
                            found_ingredient.update(**ingredient_field_values)
            return response
        else:
            return response


class RecipeSearchListView(ListView):
    http_method_names = ('get',)
    model = Recipe
    paginate_by = 10
    context_object_name = 'recipes'
    template_name = 'search.html'

    def get_queryset(self):
        kw = self.request.GET.get("kw")
        if kw:
            return self.model.objects.filter(name__iexact=kw)
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


class RecipeCreateView(SignInRequiredMixin, RecipeViewMixin, CreateView):
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


class RecipeUpdateView(SignInRequiredMixin, RecipeViewMixin, UpdateView):
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


class RecipeDetailView(DetailView):
    model = Recipe
    template_name = 'recipes/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ingredients'] = [ing.to_dict for ing in list(self.get_object().recipe_ingredients.all())]
        return context
