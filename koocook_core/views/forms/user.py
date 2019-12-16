from django.contrib.auth.models import User
from django.forms.widgets import Textarea, HiddenInput

from ...models import KoocookUser
from ...support import CustomisableForm


class BasicProfileForm(CustomisableForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class ExtendedProfileForm(CustomisableForm):
    class Meta:
        model = KoocookUser
        fields = ['preferences']
        widgets = {'preferences': HiddenInput(attrs={'v-model': 'submission'})}

    customised_field = ('user',)
