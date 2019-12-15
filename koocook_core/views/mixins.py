import json
import logging
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import reverse
from django.views.generic.edit import FormMixin, ProcessFormView

from .forms import CommentForm
from ..models import Author, RecipeIngredient, RecipeEquipment, MetaIngredient, get_client_ip

LOGGER = logging.getLogger(__name__)


class SignInRequiredMixin(LoginRequiredMixin):
    @property
    def login_url(self):
        LOGGER.info(f"An unauthenticated visitor attempted to access the authenticated page")
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
            LOGGER.info(f"{self.request.user.username} has requested an author view")
            context['current_author'] = Author.objects.get(user__user=self.request.user)
        else:
            context['current_author'] = {'id': 0}
        return context

    def get_author(self) -> Author:
        return Author.objects.get(user__user=self.request.user)

    def get_visitor_name(self) -> str:
        if self.request.user.is_authenticated:
            return f"{self.request.user.username} (User)"
        else:
            return f"Anonymous IP: {get_client_ip(self.request)}"

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
    ACTION = 'mixin'

    def process_tags(self, form):
        from ..models import Tag, TagLabel
        tags = json.loads(self.request.POST.get('tags'))
        if tags:
            for tag in tags:
                tag_body: dict = {field: tag[field] for field in tag if field
                                  in [f.name for f in Tag._meta.get_fields()]}
                if 'deleted' in tag and tag['deleted']:
                    form.instance.tag_set.remove(Tag.objects.get(pk=tag['id']))
                    # Tag.objects.get(pk=tag['id']).delete()
                else:
                    if tag['label'] != '':
                        if 'id' in tag['label']:
                            tag['label'].pop('id')
                        tag_body['label'], created = TagLabel.objects.get_or_create(**tag['label'])
                    if 'id' not in tag_body:
                        tag, created = Tag.objects.get_or_create(**tag_body)
                    else:
                        tag = Tag.objects.get(pk=tag_body['id'])
                    form.instance.tag_set.add(tag)
                    # else:
                    #     try:
                    #         obj = form.instance.tag_set.get(id=tag_body['id'])
                    #         obj.name = tag_body['name']
                    #         obj.save()
                    #     except Tag.DoesNotExist:
                    #         form.instance.tag_set.add(Tag.objects.get(pk=tag_body['id']))
        else:
            form.instance.tag_set.clear()

    def process_equipment(self, form):
        equipment = self.request.POST.get('cookware_list')
        if equipment:
            equipment = json.loads(equipment)
            created = False
            for cookware in equipment:
                form.instance.equipment_set.clear()
                if 'id' in cookware:
                    try:
                        found = RecipeEquipment.objects.get(pk=cookware['id'])
                        created = True
                    except RecipeEquipment.DoesNotExist:
                        pass
                else:
                    found, created = RecipeEquipment.objects.get_or_create(name=cookware['name'])
                if created:
                    found.name = cookware['name']
                    found.save()
                form.instance.equipment_set.add(found)

    def process_instructions(self, form):
        recipe_instructions = json.loads(self.request.POST.get('recipe_instructions'))
        if isinstance(recipe_instructions, list):
            form.instance.recipe_instructions = recipe_instructions
            form.instance.save()

    def process_media(self, form):
        images = json.loads(self.request.POST.get('image'))
        if isinstance(images, list):
            form.instance.image = images
            form.instance.save()

    # Messy
    def form_valid(self, form):
        response = super().form_valid(form)
        LOGGER.info(f"{self.get_visitor_name()} has {self.ACTION}d the recipe named {form.instance.name} #{form.instance.id}")
        self.process_instructions(form)
        self.process_equipment(form)
        self.process_tags(form)
        self.process_media(form)
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
                    ing = RecipeIngredient(**ingredient_field_values)
                    ing.save()
                    LOGGER.info(f"The ingredient {meta.name} [{ing.id}] in {form.instance.name} has been created")
                else:
                    found_ingredient = RecipeIngredient.objects.filter(pk=ingredient['id'])
                    if not found_ingredient:
                        RecipeIngredient(**ingredient_field_values).save()
                    else:
                        LOGGER.info(f"The ingredient {meta.name} [{found_ingredient[0].id}] in {form.instance.name} "
                                    f"has been altered")
                        if 'removed' in ingredient and bool(ingredient['removed']):
                            found_ingredient.delete()
                        else:
                            found_ingredient.update(**ingredient_field_values)
            return response
        else:
            return response
