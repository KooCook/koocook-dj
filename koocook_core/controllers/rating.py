from typing import Type
from django.db.models import Model

from .base import BaseController
from .decorators import apply_author_from_session
from ..models import Rating, Comment, Recipe, Post


class RatableController(BaseController):
    def __init__(self, model: Type[Model], request_fields: dict):
        self.rated_item = None
        super().__init__(model, request_fields)

    @apply_author_from_session
    def rate(self):
        rating_score = int(self.model_request_fields['rating_score'])
        rating = Rating(author=self.request_fields['author'],
                        rating_value=rating_score)
        if type(self.model) == Comment:
            rating.reviewed_comment = self.rated_item
        elif type(self.model) == Recipe:
            rating.reviewed_recipe = self.rated_item
        elif type(self.model) == Post:
            rating.reviewed_post = self.rated_item
        self.model.aggregate_rating.add_rating(rating)
