from .base import JsonRequestHandler
from .mixins import CommentControllerMixin
from .rating import RatableController
from ..models import Recipe


class RecipeController(RatableController, CommentControllerMixin):
    item_reviewed_field = 'reviewed_recipe'

    def __init__(self):
        super().__init__(Recipe, {})

    @classmethod
    def default(cls):
        return cls()


class RecipeAPIHandler(JsonRequestHandler):
    def __init__(self):
        super().__init__(RecipeController.default())
        self.handler_map = {
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
