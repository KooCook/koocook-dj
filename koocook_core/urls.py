from django.urls import path, include

from . import views

app_name = 'koocook_core'
urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search_view, name='search'),
    path('recipes/', views.RecipeCreateView.as_view(), name='recipe-create'),
    path('recipes/new', views.detail_view, name='detail'),
    path('recipes/detail', views.detail_view, name='detail'),  # Placeholder for now...
]
