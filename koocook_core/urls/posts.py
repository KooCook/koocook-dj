from django.urls import path

from ..controllers import PostHandler

app_name = 'posts'
handler = PostHandler.instance()
urlpatterns = [
    path('', handler.handle, name="all"),
    path('user/', handler.handle, name="user", kwargs={"alias": 'user'}),
    path('<int:pk>', handler.handle, name="detail"),
]
