from django import forms
from ...models import Comment


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('body',)
        exclude = ('reviewed_recipe',)
        widgets = {'body': forms.Textarea(attrs={'placeholder': 'Add a comment...'})}

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['body'].widget.attrs.pop('rows', None)
        self.fields['body'].widget.attrs.pop('cols', None)

