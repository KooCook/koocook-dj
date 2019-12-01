from django.urls import path

from ..controllers import PostHandler

app_name = 'posts'
handler = PostHandler.instance()
urlpatterns = [
    path('', handler.handle, name='view'),
    path('all/', handler.handle, name="all", kwargs={"alias": 'all'}),
    path('following/', handler.handle, name="followed-post", kwargs={"alias": 'followed-post'}),
    path('user/', handler.handle, name="user", kwargs={"alias": 'user'}),
    path('<int:pk>', handler.handle, name="detail"),
    path('<int:pk>/rate/', handler.handle, name="rate", kwargs={"alias": 'rate'}),
    path('<int:item_id>/comments', handler.handle, name='comments', kwargs={"alias": 'comment'}),
]
