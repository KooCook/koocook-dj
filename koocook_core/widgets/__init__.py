from django.forms.widgets import Widget, TextInput
from koocook_core.support.quantity import parse_quantity, Quantity
from django.utils.dateparse import parse_duration


class DurationInput(TextInput):
    template_name = 'widgets/duration_input.html'

    def __init__(self, model, attrs=None):
        self.model = model
        super().__init__(attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['model'] = self.model
        return context


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
        try:
            context['widget']['value'] = parse_quantity(context['widget']['value'])
        except AttributeError:
            context['widget']['value'] = Quantity(1, 'serving')
        context['widget']['section'] = self.section
        return context
