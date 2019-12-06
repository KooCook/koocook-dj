from django.views.generic import DetailView

from koocook_core.models import RecipeIngredient


class IngredientDetailView(DetailView):
    model = RecipeIngredient
    template_name = 'ingredients/index.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)