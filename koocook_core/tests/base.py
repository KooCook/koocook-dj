from typing import Dict, Any
from django.contrib.auth.models import User
from django.test import TestCase

from ..models import Author, KoocookUser, Post, Recipe


def create_dummy_post(user: User) -> Post:
    post = Post(body="This is a dummy post.", author=Author.objects.get(user__user=user))
    post.save()
    return post


def create_dummy_recipe(user: User):
    recipe = Recipe(name='dummy', author=Author.objects.get(user__user=user))
    recipe.image = '{"https://docs.djangoproject.com/en/2.2/ref/contrib/postgres/fields/#arrayfield"}'
    recipe.date_published = '2019-11-05 04:04:07'
    recipe.description = 'This is a description.'
    recipe.prep_time = '00:00:03'
    recipe.cook_time = '00:00:02'
    recipe.recipe_instructions = '{"This is an instruction."}'
    recipe.recipe_yield = '30 mL'
    recipe.save()
    return recipe


def create_dummy_comment_dict() -> Dict[str, Any]:
    comment_fields: Dict[str, Any] = dict()
    comment_fields['body'] = 'Chi-squared test'
    return comment_fields


def create_dummy_recipe(author: Author) -> Recipe:
    recipe = Recipe(author=author, name="Dummy recipe")
    recipe.recipe_instructions = "{}"
    recipe.save()
    return recipe


class AuthTestCase(TestCase):
    def setUp(self) -> None:
        self.username = "testuser"
        password = "123$*HCfjdksla"
        self.password = password
        self.user = User.objects.create_user(self.username, password=password)
        self.user2 = User.objects.create_user("testuser2", password=self.password)
        self.client.login(username=self.username, password=password)
        self.kc_user = KoocookUser.objects.get(user=self.user)
        self.author = Author.objects.get(user__user=self.user)
