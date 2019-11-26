from django.shortcuts import reverse
from django.test import TestCase
from django.contrib.auth.models import User

from ..models import Author, Post, Recipe


def create_dummy_post(user: User):
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


class RatingTest(TestCase):
    def setUp(self) -> None:
        self.username = "testuser"
        password = "123$*HCfjdksla"
        self.user = User.objects.create_user(self.username, password=password)
        self.client.login(username=self.username, password=password)
        self.recipe = create_dummy_recipe(self.user)
        self.post = create_dummy_post(self.user)
        self.recipe_rate_url = reverse('koocook_core:recipe-rate', args=(self.recipe.id,))
        self.post_rate_url = reverse('koocook_core:posts:rate', args=(self.post.id,))

    def test_rate_recipe_single_score(self):
        response = self.client.post(self.recipe_rate_url, {'rating_score': 3})
        self.assertContains(response, '3.0')
        self.assertEqual(response.status_code, 200)

    def test_rate_post_single_score(self):
        response = self.client.post(self.post_rate_url, {'rating_score': 1})
        self.assertContains(response, '1.0')
        self.assertEqual(response.status_code, 200)
