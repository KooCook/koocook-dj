from koocook_core.tests.base import create_dummy_post, AuthTestCase
from koocook_core.models import Comment, Post, Recipe


class CommentTest(AuthTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.comment_body = "This is a comment."

    def test_comment_post_reviewed(self):
        post = create_dummy_post(self.user)
        comment = Comment.objects.create(author=self.author,
                                         body=self.comment_body, reviewed_post=post)
        with self.subTest():
            self.assertEqual(comment.item_reviewed, post)
        with self.subTest():
            self.assertEqual(comment.as_dict["rendered"], self.comment_body)

        with self.subTest():
            comment.item_reviewed = post
            self.assertEqual(comment.item_reviewed, post)
            self.assertEqual(comment.reviewed_post, post)


