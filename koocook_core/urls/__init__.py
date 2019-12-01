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
    path('comments/', views.post_comment, name='comments-post'),
    path('comments/<int:item_id>', comment_handler.handle, name='comments'),
    path('comments/<int:pk>/rate', comment_handler.handle, name='comment-rate', kwargs={"alias": 'rate'}),
    path('recipes/<int:recipe_id>', views.handle_recipe, name='recipe'),
    path('recipes/<int:item_id>/comments', recipe_handler.handle, name='recipe-comments', kwargs={"alias": 'comment'}),
    path('recipes/<int:pk>/edit', views.RecipeUpdateView.as_view(), name='recipe-edit'),
    path('recipes/tags', views.recipe_tags, name='recipe-tags'),
    path('recipes/<int:pk>/rate', recipe_handler.handle, name='recipe-rate', kwargs={"alias": 'rate'}),
    path('recipes/new', views.RecipeCreateView.as_view(), name='recipe-create'),
    path('recipes/yours', views.UserRecipeListView.as_view(), name='recipe-user'),
] + views.serve_static()
