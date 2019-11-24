from django.urls import path

from ..controllers import PostHandler

app_name = 'posts'
handler = PostHandler.instance()
urlpatterns = [
    path('', handler.handle, name="all"),
    path('all', handler.handle, name="ajax-all", kwargs={"alias": 'all'}),
    path('user/', handler.handle, name="user", kwargs={"alias": 'user'}),
    path('following/', handler.handle, name="followee", kwargs={"alias": 'followee'}),
    path('<int:pk>', handler.handle, name="detail"),
]
