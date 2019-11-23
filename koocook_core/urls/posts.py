from django.urls import path

from ..controllers import PostHandler
from ..views import get_all_comments_for

app_name = 'posts'
handler = PostHandler.instance()
urlpatterns = [
    path('', handler.handle, name="all"),
    path('<int:pk>', handler.handle, name="detail"),
    path('<int:item_id>/comments', get_all_comments_for, name='comments'),
]
