from django.urls import path

from ..controllers import PostHandler

app_name = 'posts'
handler = PostHandler.instance()
urlpatterns = [
    path('', handler.handle, name="view"),
    path('all', handler.handle, name="ajax-all", kwargs={"alias": 'all'}),
    path('following/', handler.handle, name="followee", kwargs={"alias": 'followee'}),
    path('user/', handler.handle, name="user", kwargs={"alias": 'user'}),
    path('<int:pk>', handler.handle, name="detail"),
    path('<int:pk>/rate/', handler.handle, name="rate", kwargs={"alias": 'rate'}),
    path('<int:item_id>/comments', handler.handle, name='comments', kwargs={"alias": 'comment'}),
]
