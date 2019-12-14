from typing import Dict, Any
from django.contrib.auth.models import User
from django.test import TestCase

from ..models import Author, KoocookUser, Post, Recipe


def create_dummy_post(user: User) -> Post:
    post = Post(body="This is a dummy post.", author=Author.objects.get(user__user=user))
    post.save()
    return post


def create_dummy_recipe_body(author: Author) -> dict:
    recipe_body = {'name': 'dummy',
                   'author': author,
                   'image': '{"https://docs.djangoproject.com/en/2.2/ref/contrib/postgres/fields/#arrayfield"}',
                   'date_published': '2019-11-05 04:04:07',
                   'description': 'This is a description.',
                   'prep_time': '00:00:03',
                   'cook_time': '00:00:02',
                   'recipe_instructions': '{"This is an instruction."}',
                   'recipe_yield': '30 mL'}
    return recipe_body


def create_dummy_recipe(author: Author) -> Recipe:
    recipe = Recipe(**create_dummy_recipe_body(author))
    recipe.save()
    return recipe





def create_dummy_comment_dict() -> Dict[str, Any]:
    comment_fields: Dict[str, Any] = dict()
    comment_fields['body'] = 'Chi-squared test'
    return comment_fields


class AuthTestCase(TestCase):
    def setUp(self) -> None:
        self.username = "testuser"
        password = "123$*HCfjdksla"
        self.password = password
        self.user = User.objects.create_user(self.username, password=password)
        self.user2 = User.objects.create_user("testuser2", password=self.password)
        self.client.login(username=self.username, password=password)
        self.author = Author.objects.get(user__user=self.user)

    @property
    def kc_user(self):
        return KoocookUser.objects.get(user=self.user)
