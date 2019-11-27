from django.urls import include, path

from .. import views

app_name = 'koocook_core'
urlpatterns = [
    path('', views.index, name='index'),
    path('posts/', include('koocook_core.urls.posts'), name='posts'),
    path('search/', views.RecipeSearchListView.as_view(), name='search'),
    path('comments/', views.post_comment, name='comments-post'),
    path('comments/<int:item_id>', views.get_all_comments_for, name='comments'),
    path('profile/', include('koocook_core.urls.profile'), name='profile'),
    path('recipes/<int:recipe_id>', views.handle_recipe, name='recipe'),
    path('recipes/<int:item_id>/comments', views.get_all_comments_for, name='recipe-comments'),
    path('recipes/<int:pk>/edit', views.RecipeUpdateView.as_view(), name='recipe-edit'),
    path('recipes/tags', views.recipe_tags, name='recipe-create'),
    path('recipes/new', views.RecipeCreateView.as_view(), name='recipe-create'),
    path('recipes/yours', views.UserRecipeListView.as_view(), name='recipe-user'),
    path('recipes/detail', views.RecipeDetailView.as_view(), name='detail'),  # Placeholder for now...
]
