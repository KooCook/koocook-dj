import json
from django.http import HttpResponse, HttpResponseForbidden, HttpRequest
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import reverse
from django.views.generic.edit import FormMixin, ProcessFormView

from .forms import CommentForm
from ..models import Author, RecipeIngredient, MetaIngredient


class SignInRequiredMixin(LoginRequiredMixin):
    @property
    def login_url(self):
        return reverse('social:begin', args=['google-oauth2'])


class AuthAuthorMixin:

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_author'] = Author.objects.get(user__user=self.request.user)
        return context

    def form_valid(self, form):
        form.instance.author = Author.objects.get(user__user=self.request.user)
        return super().form_valid(form)


class CommentWidgetMixin(AuthAuthorMixin, FormMixin):
    form_class = CommentForm
    #
    # def post(self, request, *args, **kwargs):
    #     self.object = self.get_object()
    #     form = self.get_form()
    #     if form.is_valid():
    #         form.instance.reviewed_recipe = self.object
    #         return self.form_valid(form)
    #     else:
    #         return self.form_invalid(form)
    #
    # def form_valid(self, form):
    #     return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comment_set.all()
        context['comment_form'] = self.get_form()
        return context


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
