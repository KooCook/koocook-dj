from django import forms
from django.forms.widgets import HiddenInput
from ...models import Feedback


class FeedbackForm(forms.ModelForm):
    customised_field = ['author']

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = Feedback
        fields = '__all__'
        exclude = ('author', 'date_published', 'status')
        widgets = {'image': HiddenInput(), 'video': HiddenInput()}

    @property
    def vanilla_fields(self):
        return [field for field in self if not (field.name in self.customised_field or field.is_hidden)]
