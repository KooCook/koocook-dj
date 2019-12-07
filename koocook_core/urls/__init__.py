from django.urls import include, path

from .. import views
from ..controllers import CommentAPIHandler, RecipeAPIHandler
recipe_handler = RecipeAPIHandler.instance()
comment_handler = CommentAPIHandler.instance()

app_name = 'koocook_core'
urlpatterns = [
    path('', views.index, name='index'),
    path('posts/', include('koocook_core.urls.posts'), name='posts'),
    path('profile/', include('koocook_core.urls.profile'), name='profile'),
    path('search/', views.RecipeSearchListView.as_view(), name='search'),
    # path('comments/', views.post_comment, name='comments-post'),
    path('comments/<int:item_id>', comment_handler.handle, name='comments'),
    path('comments/<int:item_id>/comment', comment_handler.handle, name='comment-self', kwargs={"alias": 'comment'}),
    path('comments/<int:pk>/rate', comment_handler.handle, name='comment-rate', kwargs={"alias": 'rate'}),
    path('profile/', include('koocook_core.urls.profile'), name='profile'),
    path('cookware/', views.RecipeEquipmentView.as_view(), name='equipment-all'),
    path('cookware/<int:pk>', views.RecipeEquipmentDetailView.as_view(), name='equipment'),
    path('ingredients/', views.RecipeIngredientsView.as_view(), name='ingredients'),
    path('ingredients/<int:pk>', views.IngredientDetailView.as_view(), name='ingredient'),
    path('recipes/', include('koocook_core.urls.recipes'), name='recipes'),
    path('recipes/', views.PreferredRecipeStreamView.as_view(), name='recipe-all'),
    path('recipes/unit_conv', recipe_handler.handle, name='recipe-unit-conv', kwargs={"alias": 'unit_conv'}),
    path('recipes/<int:recipe_id>', views.handle_recipe, name='recipe'),
    path('recipes/<int:item_id>/comments', recipe_handler.handle, name='recipe-comments', kwargs={"alias": 'comment'}),
    path('recipes/<int:pk>/edit', views.RecipeUpdateView.as_view(), name='recipe-edit'),
    path('recipes/tags', views.recipe_tags, name='recipe-tags'),
    path('recipes/<int:pk>/rate', recipe_handler.handle, name='recipe-rate', kwargs={"alias": 'rate'}),
    path('recipes/new', views.RecipeCreateView.as_view(), name='recipe-create'),
    path('recipes/yours', views.UserRecipeListView.as_view(), name='recipe-user'),
] + views.serve_static()
