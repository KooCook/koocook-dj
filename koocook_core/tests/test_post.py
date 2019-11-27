from django.test import TestCase
from ..controllers import CommentController, PostController
from .fixtures import create_dummy_post


class PostCommentControllerTest(TestCase):
    controller = PostController()

    def setUp(self) -> None:
        self.post = create_dummy_post()

    def test_add_comment(self):
        self.controller.comment()
