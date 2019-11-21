from django.urls import include, path

from .. import views

app_name = 'koocook_core'
urlpatterns = [
    path('', views.index, name='index'),
    path('posts/', include('koocook_core.urls.posts'), name='posts'),
    path('search/', views.RecipeSearchListView.as_view(), name='search'),
    path('recipes/<int:recipe_id>', views.handle_recipe, name='recipe'),
    path('recipes/<int:pk>/edit', views.RecipeUpdateView.as_view(), name='recipe-edit'),
    path('recipes/new', views.RecipeCreateView.as_view(), name='recipe-create'),
    path('recipes/yours', views.UserRecipeListView.as_view(), name='recipe-user'),
    path('recipes/detail', views.RecipeDetailView.as_view(), name='detail'),  # Placeholder for now...
]
