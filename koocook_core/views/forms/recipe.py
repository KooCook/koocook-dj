from django import forms
from django.forms.widgets import HiddenInput
from ...widgets import QuantityInput, DurationInput
from ...models import Recipe
from ...support import CustomisableForm


class RecipeForm(CustomisableForm):
    customised_field = ('author', 'name')
    tags = forms.CharField(widget=forms.HiddenInput(
        attrs={'v-model': 'JSON.stringify(tags)'}))

    class Meta:
        model = Recipe
        fields = '__all__'
        exclude = ('aggregate_rating', 'author',
                   'date_published', 'equipment_set', 'tag_set')
        widgets = {'image': HiddenInput(), 'video': HiddenInput(),
                   'recipe_yield': QuantityInput('serving'),
                   'prep_time': DurationInput(model='prep_time'),
                   'cook_time': DurationInput(model='cook_time')}
