from django.contrib.auth.models import User
from django.forms.widgets import Textarea, HiddenInput

from ...models import KoocookUser
from ...support import CustomisableForm


class BasicProfileForm(CustomisableForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)


class ExtendedProfileForm(CustomisableForm):
    class Meta:
        model = KoocookUser
        fields = ['preferences']

        widgets = {'preferences': HiddenInput(attrs={'v-model': 'submission'})}

    customised_field = ('user',)

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    @property
    def vanilla_fields(self):
        return [field for field in self if not (field.name in self.customised_field or field.is_hidden)]
