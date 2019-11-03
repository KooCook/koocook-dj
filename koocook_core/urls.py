from django.urls import path, include

from . import views

app_name = 'koocook_core'
urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search_view, name='search'),
    path('recipes/<int:id>/', views.detail_view, name='detail'),
]
