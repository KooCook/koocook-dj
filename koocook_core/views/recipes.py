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


class RecipeSearchListView(AuthAuthorMixin, ListView):
    http_method_names = ('get',)
    model = Recipe
    paginate_by = 10
    context_object_name = 'recipes'
    template_name = 'search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.GET.get("popular"):
            context['search_filter'] = 'popular'
        elif self.request.GET.get("name_asc"):
            context['search_filter'] = 'name'
        else:
            context['search_filter'] = 'date'
        return context

    def get_queryset(self):
        popular = self.request.GET.get("popular")
        kw = self.request.GET.get("kw")
        if kw:
            query_set = self.model.objects.filter(name__icontains=kw)
        else:
            query_set = self.model.objects.all()
        if self.request.GET.get("name_asc"):
            query_set = query_set.order_by("name")
        else:
            query_set = query_set.order_by("-date_published")
        if popular:
            query_set = sorted(query_set,
                               key=lambda t: t.popularity_score,
                               reverse=True)
        return query_set


class UserRecipeListView(SignInRequiredMixin, ListView):
    model = Recipe
    template_name = 'recipes/user.html'
    context_object_name = "user_recipes"

    def get_queryset(self):
        # try:
        author = Author.objects.get(user__user=self.request.user)
        # except ObjectDoesNotExist:
        #     author = Author(user=KoocookUser.objects.get(user=self.request.user))
        #     author.save()
        return Recipe.objects.filter(author=author).order_by('-date_published')


class RecipeCreateView(RecipeViewMixin, CreateView):
    http_method_names = ['post', 'get']
    form_class = RecipeForm
    template_name = 'recipes/create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_success_url(self):
        return reverse('koocook_core:recipe-user')


class FractionEncoder(json.JSONEncoder):

    def default(self, obj):
        if hasattr(obj, 'as_dict'):
            return obj.as_dict
        else:
            return str(obj)


class RecipeUpdateView(RecipeViewMixin, UpdateView):
    form_class = RecipeForm
    model = Recipe
    # fields = '__all__'  # ['name']
    template_name = 'recipes/update.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user != self.get_object().author.dj_user:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('koocook_core:recipe-user')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ingredients'] = json.dumps([ing.to_dict for ing in list(self.get_object().recipe_ingredients.all())],
                                            cls=FractionEncoder)
        context['tags'] = json.dumps([ing.as_dict() for ing in list(self.get_object().tag_set.all())], cls=ModelEncoder)
        return context


class RecipeDetailView(CommentWidgetMixin, DetailView):
    model = Recipe
    template_name = 'recipes/detail.html'
    object: Recipe

    def get(self, request, *args, **kwargs):
        from django.db.utils import IntegrityError
        from ..models.recipe import RecipeVisit
        from ..models import KoocookUser
        response = super().get(request, *args, **kwargs)
        if self.request.user.is_authenticated:
            user: KoocookUser = KoocookUser.from_dj_user(self.request.user)
            visit = RecipeVisit.associate_recipe_with_user(user, self.object)
            ip = visit.add_ip_address(self.request, self.object)
            # try:
            #     RecipeVisit.objects.get(ip_address=ip, recipe=self.object).delete()
            # except RecipeVisit.DoesNotExist:
            #     pass
            # visit.ip_address = ip
            visit.save()
        else:
            RecipeVisit.associate_recipe_with_ip_address(self.request, self.object)
        return response

    # def get_success_url(self):
    #     return self.request.path

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ingredients'] = [ing.to_dict for ing in list(self.get_object().recipe_ingredients.all())]
        return context


class PreferredRecipeStreamView(AuthAuthorMixin, ListView):
    model = Recipe
    queryset = Recipe.objects.prefetch_related('author')
    paginate_by = 10
    template_name = "recipes/suggested.html"

    @property
    def preferred_tags(self):
        from ..support import PreferenceManager
        if self.request.user.is_authenticated:
            preferences = PreferenceManager.from_koocook_user(self.get_author().user)
        else:
            preferences = PreferenceManager()
        return preferences.get("preferred_tags")

    def get_context_data(self, **kwargs):
        from koocook_core.models import Tag
        context = super().get_context_data(**kwargs)
        context['tag_set'] = Tag.objects.filter(name__in=[tag["name"] for tag in self.preferred_tags.setting])
        return context

    def get_queryset(self):
        tags = self.preferred_tags
        if len(tags.setting) > 0:
            converted_exact_tag_set_names = []
            for tag in tags.setting:
                converted_exact_tag_set_names.append(tag["name"])
            return Recipe.objects.filter(tag_set__name__in=converted_exact_tag_set_names)
        else:
            return Recipe.objects.all()
