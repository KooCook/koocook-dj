from django import forms
from django.forms.widgets import HiddenInput
from ...models import Recipe


class RecipeForm(forms.ModelForm):
    customised_field = ['name', 'author']
    tags = forms.CharField(widget=forms.HiddenInput(attrs={'v-model': 'JSON.stringify(tags)'}))

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # self.fields['author'].disabled = True

    class Meta:
        model = Recipe
        fields = '__all__'
        widgets = {'tag_set': forms.HiddenInput()}
        exclude = ('author', 'date_published')

    @property
    def vanilla_fields(self):
        return [field for field in self if not (field.name in self.customised_field or field.is_hidden)]
