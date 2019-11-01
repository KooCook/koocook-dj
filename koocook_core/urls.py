from django.urls import include, path

from . import views

app_name = 'koocook_core'
urlpatterns = [
    path('', views.index, name='index')
]
