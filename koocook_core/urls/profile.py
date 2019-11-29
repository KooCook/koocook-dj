from django.urls import path

from ..controllers import UserHandler

app_name = 'profile'
handler = UserHandler.instance()
urlpatterns = [
    path('', handler.handle, name="all", kwargs={"alias": 'index'}),
    path('follow/', handler.handle, name="follow", kwargs={"alias": 'follow'}),
    path('unfollow/', handler.handle, name="unfollow", kwargs={"alias": 'unfollow'}),
]
