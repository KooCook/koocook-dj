import json
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


class SignInRequiredMixin(LoginRequiredMixin):
    @property
    def login_url(self):
        return reverse('social:begin', args=['google-oauth2'])


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
        else:
            context['search_filter'] = 'name'
        return context

    def get_queryset(self):
        popular = self.request.GET.get("popular")
        kw = self.request.GET.get("kw")
        if kw:
            query_set = self.model.objects.filter(name__icontains=kw).order_by("name")
        else:
            query_set = self.model.objects.all().order_by("date_published")
        if popular:
            query_set.order_by('aggregate_rating__rating_value')
            query_set = sorted(query_set, key=lambda t: t.view_count, reverse=True)
        return query_set


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


class RecipeCreateView(SignInRequiredMixin, AuthAuthorMixin, RecipeViewMixin, CreateView):
    http_method_names = ('post', 'get')
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


class RecipeUpdateView(SignInRequiredMixin, AuthAuthorMixin, RecipeViewMixin, UpdateView):
    model = Recipe
    form_class = RecipeForm
    template_name = 'recipes/update.html'


    def get_success_url(self):
        return reverse('koocook_core:recipe-user')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['images'] = json.dumps(self.get_object().image)
        context['ingredients'] = json.dumps([ing.to_dict for ing in list(self.get_object().recipe_ingredients.all())],
                                            cls=FractionEncoder)
        context['instructions'] = json.dumps([{'text': ing, 'editing': False}
                                              for ing in list(self.get_object().recipe_instructions)])
        context['tags'] = json.dumps([ing.as_dict for ing in list(self.get_object().tag_set.all())],
                                     cls=ModelEncoder)
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
            visit.save()
            try:
                visit.add_ip_address(self.request)
                visit.save()
            except IntegrityError:
                pass
        else:
            try:
                RecipeVisit.associate_recipe_with_ip_address(self.request, self.object).save()
            except IntegrityError:
                pass
        return response

    # def get_success_url(self):
    #     return self.request.path

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ingredients'] = [ing.to_dict for ing in list(self.get_object().recipe_ingredients.all())]
        return context
