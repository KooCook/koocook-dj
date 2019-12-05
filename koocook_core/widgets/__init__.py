from django.forms.widgets import Widget
from koocook_core.support.quantity import parse_quantity

class RecipeTagInput(Widget):
    template_name = 'widgets/recipe_tag_input.html'

    def __init__(self, model, attrs=None):
        self.model = model
        super().__init__(attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['model'] = self.model
        return context


class QuantityInput(Widget):
    template_name = 'widgets/quantity_input.html'

    def __init__(self, section, attrs=None):
        self.section = section
        super().__init__(attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['value'] = parse_quantity(context['widget']['value'])
        context['widget']['section'] = self.section
        return context
