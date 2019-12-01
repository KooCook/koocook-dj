from django.test import TestCase
from django.shortcuts import reverse
from django.http import HttpRequest, JsonResponse
from koocook_core.models import Author, Comment, Post
from koocook_core.controllers import CommentController, PostController
from koocook_core.tests.base import AuthTestCase, create_dummy_post, create_dummy_comment_dict


class PostTest(AuthTestCase):
    model = Post
    controller = PostController()
    dummy_post_body = "This is a dummy post."

    def setUp(self) -> None:
        super().setUp()
        self.post = create_dummy_post(self.user)
        self.comment = Comment.objects.create(author=Author.objects.get(user__user=self.user),
                                              reviewed_post=self.post)
        self.comment_dict = create_dummy_comment_dict()
        self.controller.request = HttpRequest()
        self.controller.request.user = self.user
        self.controller.request_fields["user"] = self.user
        self.controller.request_fields["author"] = self.author

    def test_view_all_posts(self):
        response = self.client.get(reverse('koocook_core:posts:view'))
        with self.subTest():
            self.assertEqual(list(response.context['posts']), list(self.model.objects.all()))
            self.assertEqual(response.status_code, 200)

    def test_view_all_guest_posts(self):
        self.client.logout()
        response = self.client.get(reverse('koocook_core:posts:view'))
        with self.subTest():
            self.assertEqual(list(response.context['posts']), list(self.model.objects.all()))
            self.assertEqual(response.status_code, 200)

    def test_controller_add_comment(self):
        self.controller.request_fields.update(self.comment_dict)
        response = self.controller.comment(item_id=self.post.id)
        with self.subTest():
            self.assertEqual(response.obj.body.source, self.comment_dict['body'])
            self.assertEqual(response.obj.reviewed_post, self.post)

    def test_controller_create_post(self):
        self.controller.request_fields["body"] = self.dummy_post_body
        response = self.controller.create()
        with self.subTest("Creating post with PostController test"):
            self.assertEqual(response.obj.body.source, self.dummy_post_body)
            self.assertEqual(response.obj.author, self.author)

    def test_controller_edit_post(self):
        edited_post_body = "This is an edited post."
        self.controller.request_fields["body"] = edited_post_body
        response = self.controller.update_post(pk=self.post.id)
        with self.subTest("Editing post with PostController test"):
            self.assertEqual(response.obj.body.source, edited_post_body)
            self.assertEqual(response.obj.author, self.author)

    def test_controller_delete_post(self):
        response = self.controller.delete_post(pk=self.post.id)
        with self.subTest("Deleting post with PostController test"):
            self.assertEqual("Deleted", response.status_text)
        with self.subTest():
            with self.assertRaises(Post.DoesNotExist):
                Post.objects.get(pk=response.obj.id)
