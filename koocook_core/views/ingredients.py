from django.views.generic import DetailView

from koocook_core.models import MetaIngredient


class IngredientDetailView(DetailView):
    model = MetaIngredient
    template_name = 'ingredients/index.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)
