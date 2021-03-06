from django.urls import path
from .. import views
from ..controllers import RecipeAPIHandler
recipe_handler = RecipeAPIHandler.instance()

app_name = 'recipes'
urlpatterns = [
    path('', views.PreferredRecipeStreamView.as_view(), name='suggested'),
    path('<int:recipe_id>', views.handle_recipe, name='detail'),
    path('new', views.RecipeCreateView.as_view(), name='create'),
    path('yours', views.UserRecipeListView.as_view(), name='user'),
    path('<int:item_id>/comments', recipe_handler.handle, name='comments', kwargs={"alias": 'comment'}),
    path('<int:pk>/edit', views.RecipeUpdateView.as_view(), name='edit'),
    path('tags', views.recipe_tags, name='tags'),
    path('<int:pk>/rate', recipe_handler.handle, name='rate', kwargs={"alias": 'rate'}),
    path('unit_conv', recipe_handler.handle, name='unit-conv', kwargs={"alias": 'unit_conv'}),
    path('ingredients', views.recipe_ingredients, name='ingredients'),
    path('equipment', views.recipe_equipment, name='equipment'),
    path('authors', views.recipe_authors, name='authors'),
]
