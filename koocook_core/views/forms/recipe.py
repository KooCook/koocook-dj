from django import forms
from django.forms.widgets import HiddenInput
from ...models import Recipe


class RecipeForm(forms.ModelForm):
    customised_field = ['name', 'author']

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # self.fields['author'].disabled = True

    class Meta:
        model = Recipe
        fields = '__all__'
        exclude = ('date_published', 'aggregate_rating')
        widgets = {'image': HiddenInput(), 'video': HiddenInput()}

    @property
    def vanilla_fields(self):
        return [field for field in self if not (field.name in self.customised_field or field.is_hidden)]
