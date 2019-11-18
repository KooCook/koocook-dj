from django.urls import path

from ..controllers import UserHandler
from ..views import UserSettingsInfoView

app_name = 'profile'
handler = UserHandler.instance()
urlpatterns = [
    path('', handler.handle, name="info"),
    path('preferences/', handler.handle, name="pref", kwargs={"alias": 'pref'}),
    path('follow/', handler.handle, name="follow", kwargs={"alias": 'follow'}),
    path('unfollow/', handler.handle, name="unfollow", kwargs={"alias": 'unfollow'}),
]
