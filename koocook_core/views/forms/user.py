from django import forms
from django.contrib.auth.models import User
from ...models import KoocookUser


class BasicProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # self.fields['author'].disabled = True

    @property
    def vanilla_fields(self):
        return [field for field in self if not (field.name in self.customised_field or field.is_hidden)]


class ExtendedProfileForm(forms.ModelForm):
    class Meta:
        model = KoocookUser
        fields = ['preferences', 'user_settings']

    customised_field = ['user']

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # self.fields['author'].disabled = True

    @property
    def vanilla_fields(self):
        return [field for field in self if not (field.name in self.customised_field or field.is_hidden)]
