from django.urls import path

from ..controllers import PostHandler

app_name = 'posts'
handler = PostHandler.instance()
urlpatterns = [
    path('', handler.handle, name="all"),
    path('<int:pk>', handler.handle, name="detail"),
]
