import json
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import reverse
from django.views.generic.edit import FormMixin, ProcessFormView

from .forms import CommentForm
from ..models import Author, RecipeIngredient, RecipeEquipment, MetaIngredient


class SignInRequiredMixin(LoginRequiredMixin):
    @property
    def login_url(self):
        return reverse('social:begin', args=['google-oauth2'])

    def get_success_url(self):
        return self.request.path


class PreferencesMixin(SignInRequiredMixin):
    def form_valid(self, form):
        self.object.formal_preferences.update_from_json(self.request.POST["preferences"])
        response = super().form_valid(form)
        return response


class AuthAuthorMixin:

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['current_author'] = Author.objects.get(user__user=self.request.user)
        else:
            context['current_author'] = {'id': 0}
        return context

    def get_author(self) -> Author:
        return Author.objects.get(user__user=self.request.user)

    def form_valid(self, form):
        form.instance.author = self.get_author()
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


class RecipeViewMixin(SignInRequiredMixin, AuthAuthorMixin):

    def process_equipment(self, form):
        equipment = json.loads(self.request.POST.get('cookware_list'))
        if equipment:
            for cookware in equipment:
                found, created = RecipeEquipment.objects.get_or_create(name=cookware)

                if 'id' in cookware:
                    found = RecipeEquipment.objects.filter(pk=cookware['id'])
                    if not found:
                        this_equipment = RecipeEquipment(name=cookware)
                        this_equipment.save()
                        form.instance.equipment_set.add(this_equipment)
                    else:
                        if 'removed' in cookware and bool(cookware['removed']):
                            form.instance.equipment_set.remove(found)
                            found.delete()
                        else:
                            found.update(name=cookware)
                else:
                    form.instance.equipment_set.add(found)

    # Messy
    def form_valid(self, form):
        from ..models import Tag, TagLabel
        response = super().form_valid(form)
        self.process_equipment(form)
        tags = json.loads(self.request.POST.get('tags'))
        if tags:
            for tag in tags:
                tag_body: dict = {field: tag[field] for field in tag if field
                                  in [f.name for f in Tag._meta.get_fields()]}
                if 'deleted' in tag and tag['deleted']:
                    form.instance.tag_set.remove(Tag.objects.get(pk=tag['id']))
                    Tag.objects.get(pk=tag['id']).delete()
                else:
                    if tag['label'] != '':
                        if 'id' in tag['label']:
                            tag['label'].pop('id')
                        tag_body['label'] = TagLabel.objects.create(**tag['label'])
                    if 'id' not in tag_body:
                        form.instance.tag_set.add(Tag.objects.create(**tag_body))
                    else:
                        try:
                            obj = form.instance.tag_set.get(id=tag_body['id'])
                            obj.name = tag_body['name']
                            obj.save()
                        except Tag.DoesNotExist:
                            form.instance.tag_set.add(Tag.objects.get(pk=tag_body['id']))
        else:
            form.instance.tag_set.clear()
        form.instance.save()

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
