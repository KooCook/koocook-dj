from django import forms
from ...models import Recipe
from ...support import CustomisableForm


class RecipeForm(CustomisableForm):
    customised_field = ('author', 'name')
    tags = forms.CharField(widget=forms.HiddenInput(attrs={'v-model': 'JSON.stringify(tags)'}))

    class Meta:
        model = Recipe
        fields = '__all__'
        exclude = ('aggregate_rating', 'author', 'date_published', 'tag_set')
