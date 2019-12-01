from .base import JsonRequestHandler
from .mixins import CommentControllerMixin
from .rating import RatableController
from ..models import Comment


class CommentController(RatableController, CommentControllerMixin):
    item_reviewed_field = 'reviewed_comment'

    @classmethod
    def default(cls):
        return cls()

    def __init__(self):
        super().__init__(Comment, {})


class CommentAPIHandler(JsonRequestHandler):
    def __init__(self):
        super().__init__(CommentController.default())
        self.handler_map = {
            'GET': 'get_all_comments_of_item_id',
            'POST': 'comment',
            'PATCH': 'update',
            'comment': {
                'GET': 'get_all_comments_of_item_id',
                'POST': 'comment'
            },
            'rate': {
                'POST': 'rate'
            }
        }

    @classmethod
    def instance(cls):
        return cls()
