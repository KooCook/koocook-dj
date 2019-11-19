from django import forms
from ...support import CustomisableForm

from ...models import Recipe


class RecipeForm(CustomisableForm):
    customised_field = ('name', 'author')

    class Meta:
        model = Recipe
        fields = '__all__'
