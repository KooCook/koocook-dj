from django import forms
from ...models import Post


class PostForm(forms.ModelForm):
    customised_field = ['author']

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # self.fields['author'].disabled = True

    class Meta:
        model = Post
        fields = '__all__'
        exclude = ('author', 'date_published')

    @property
    def vanilla_fields(self):
        return [field for field in self if not (field.name in self.customised_field or field.is_hidden)]
