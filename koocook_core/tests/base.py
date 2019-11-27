from django.contrib.auth.models import User

from ..models import Author, Post


def create_dummy_post(user: User):
    post = Post(body="This is a dummy post.", author=Author.objects.get(user__user=user))
    post.save()
    return post
