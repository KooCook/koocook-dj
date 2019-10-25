from django.urls import path, include

from . import views

app_name = 'koocook_core'
urlpatterns = [
    path('', views.index, name='index')
]
