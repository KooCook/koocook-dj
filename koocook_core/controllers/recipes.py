from .base import BaseHandler, JsonRequestHandler
from .rating import RatableController
from ..models import Recipe


class RecipeController(RatableController):
    def __init__(self):
        super().__init__(Recipe, {})

    @classmethod
    def default(cls):
        return cls()


class RecipeAPIHandler(JsonRequestHandler):
    def __init__(self):
        super().__init__(RecipeController.default())
        self.handler_map = {
            'rate': {
                'POST': 'rate'
            }
        }

    @classmethod
    def instance(cls):
        return cls()
