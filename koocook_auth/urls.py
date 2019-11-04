from django.urls import include, path

from . import views

app_name = 'koocook_auth'
urlpatterns = [
    path('logout', views.logout_view, name='logout'),
]
