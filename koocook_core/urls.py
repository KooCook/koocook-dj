from django.urls import path, re_path

from . import views

app_name = 'koocook_core'
urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search_view, name='search')
]
