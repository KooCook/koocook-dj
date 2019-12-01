from django.forms.widgets import Widget


class RecipeTagInput(Widget):
    template_name = 'widgets/recipe_tag_input.html'

    def __init__(self, model, attrs=None):
        self.model = model
        super().__init__(attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['model'] = self.model
        return context

