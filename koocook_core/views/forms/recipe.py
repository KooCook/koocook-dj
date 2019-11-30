from django import forms
from django.forms.widgets import HiddenInput
from ...models import Recipe
from ...support import CustomisableForm

class RecipeForm(forms.ModelForm):
    customised_field = ['name', 'author']
    tags = forms.CharField(widget=forms.HiddenInput(attrs={'v-model': 'JSON.stringify(tags)'}))

class RecipeForm(CustomisableForm):
    customised_field = ('name', 'author')

    class Meta:
        model = Recipe
        fields = '__all__'
        exclude = ('aggregate_rating', 'author', 'date_published', 'tag_set')

    @property
    def vanilla_fields(self):
        return [field for field in self if not (field.name in self.customised_field or field.is_hidden)]
