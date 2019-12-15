from django.urls import path

from ..controllers import UserHandler

app_name = 'profile'
handler = UserHandler.instance()
urlpatterns = [
    path('', handler.handle, name="info"),
    path('preferences/', handler.handle, name="pref", kwargs={"alias": 'pref'}),
    path('preferences/set', handler.handle, name="pref-set", kwargs={"alias": 'pref:set'}),
    path('follow/', handler.handle, name="follow", kwargs={"alias": 'follow'}),
    path('unfollow/', handler.handle, name="unfollow", kwargs={"alias": 'unfollow'}),
]
