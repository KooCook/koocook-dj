from django.shortcuts import reverse
from django.test import TestCase
from django.contrib.auth.models import User

from ..models import Author, AggregateRating, Post, Recipe
from ..controllers import PostController
from .base import create_dummy_post, create_dummy_recipe, AuthTestCase


def get_lazy_model_object(model_cls, obj_id):
    return model_cls.objects.get(pk=obj_id)


class RatingTest(AuthTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.recipe = create_dummy_recipe(self.author)
        self.post = create_dummy_post(self.user)
        self.client.login(username=self.user2.username, password=self.password)
        self.recipe_rate_url = reverse('koocook_core:recipes:rate', args=(self.recipe.id,))
        self.post_rate_url = reverse('koocook_core:posts:rate', args=(self.post.id,))

    def test_empty_reviewable_model_creation(self):
        recipe = create_dummy_recipe(self.author)
        self.assertEqual(recipe.aggregate_rating.rating_value, 0)
        self.assertTrue(isinstance(recipe.aggregate_rating, AggregateRating))

    def test_compare_rating_str(self):
        rating = AggregateRating(rating_value=3)
        self.assertEqual(str(rating), str(rating.rating_value))

    def test_rate_item_of_oneself(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.post(self.recipe_rate_url, {'rating_score': 3})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(get_lazy_model_object(Recipe, self.recipe.id).aggregate_rating.rating_count, 0)

    def test_rate_recipe_single_score(self):
        response = self.client.post(self.recipe_rate_url, {'rating_score': 3})
        self.assertContains(response, '3.0')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_lazy_model_object(Recipe, self.recipe.id).aggregate_rating.rating_count, 1)

    def test_rate_post_single_score(self):
        response = self.client.post(self.post_rate_url, {'rating_score': 1})
        self.assertContains(response, '1.0')
        self.assertEqual(response.status_code, 200)

    def test_rate_multiple(self):
        response = self.client.post(self.recipe_rate_url, {'rating_score': 5})
        with self.subTest("First rate"):
            self.assertContains(response, '5.0')
            recipe = get_lazy_model_object(Recipe, self.recipe.id)
            self.assertEqual(recipe.aggregate_rating.rating_value, 5)
            self.assertEqual(response.status_code, 200)

        response = self.client.post(self.recipe_rate_url, {'rating_score': 3})
        with self.subTest("Second rate of the multiple rating test"):
            recipe = get_lazy_model_object(Recipe, self.recipe.id)
            self.assertContains(response, '3.0')
            self.assertEqual(recipe.aggregate_rating.rating_value, 3)
            self.assertEqual(recipe.aggregate_rating.rating_count, 1)
            self.assertEqual(response.status_code, 200)

        response = self.client.post(self.post_rate_url, {'rating_score': 4})
        with self.subTest("First rate"):
            self.assertContains(response, '4.0')
            post = get_lazy_model_object(Post, self.post.id)
            self.assertEqual(post.aggregate_rating.rating_value, 4)
            self.assertEqual(response.status_code, 200)

        response = self.client.post(self.post_rate_url, {'rating_score': 2})
        with self.subTest("Second rate of the multiple rating on a Post test"):
            post = get_lazy_model_object(Post, self.post.id)
            self.assertContains(response, '2.0')
            self.assertEqual(post.aggregate_rating.rating_value, 2)
            self.assertEqual(post.aggregate_rating.rating_count, 1)
            self.assertEqual(response.status_code, 200)

