from django.urls import path, include

from . import views

app_name = 'koocook_auth'
urlpatterns = [
    path('logout', views.logout_view, name='logout'),
]
