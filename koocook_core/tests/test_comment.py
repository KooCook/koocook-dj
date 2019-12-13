from django.shortcuts import reverse

from koocook_core.tests.base import create_dummy_post, create_dummy_recipe, AuthTestCase
from koocook_core.models import Comment, Post, Recipe
from koocook_core.support.markdown import MarkdownSource


class CommentTest(AuthTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.comment_body = MarkdownSource("This is a comment.")

    def test_comment_replies(self):
        comment = Comment.objects.create(author=self.author,
                                         body=self.comment_body)
        response = self.client.post(reverse('koocook_core:comments', kwargs={'item_id': comment.id}), {
            "author": self.author,
            "body": self.comment_body
        })
        with self.subTest():
            reviewed_comment = comment.comment_set.all()[0]
            self.assertEqual(comment, reviewed_comment.reviewed_comment)
            self.assertEqual(reviewed_comment.body.source, self.comment_body.source)
            self.assertEqual(reviewed_comment.body.rendered, self.comment_body.rendered)

    def test_comment_post_reviewed(self):
        post = create_dummy_post(self.user)
        comment = Comment.objects.create(author=self.author,
                                         body=self.comment_body, reviewed_post=post)
        with self.subTest():
            self.assertEqual(comment.item_reviewed, post)
        with self.subTest():
            self.assertEqual(comment.as_dict()["rendered"], self.comment_body.rendered)
        with self.subTest():
            self.assertEqual(comment.rendered, self.comment_body.rendered)
        with self.subTest():
            comment.item_reviewed = post
            self.assertEqual(comment.item_reviewed, post)
            self.assertEqual(comment.reviewed_post, post)

    def test_comment_recipe_reviewed(self):
        recipe = create_dummy_recipe(self.author)
        response = self.client.post(reverse('koocook_core:recipes:comments', kwargs={'item_id': recipe.id}), {
            "body": self.comment_body
        })
        with self.subTest():
            self.assertEqual(response.json()["current"]["body"], self.comment_body.source)


