from typing import Type
from django.db.models import Model

from .base import BaseController, ControllerResponse
from .decorators import apply_author_from_session
from ..models import Rating, Comment, Recipe, Post


class RatableController(BaseController):
    def __init__(self, model: Type[Model], request_fields: dict):
        super().__init__(model, request_fields)

    @apply_author_from_session
    def rate(self, pk: int):
        item_reviewed = self.model.objects.get(pk=pk)
        rating_score = int(self.request_fields['rating_score'])
        rating = Rating(author=self.request_fields['author'],
                        rating_value=rating_score)
        if self.model == Comment:
            rating.reviewed_comment = item_reviewed
        elif self.model == Recipe:
            rating.reviewed_recipe = item_reviewed
        elif self.model == Post:
            rating.reviewed_post = item_reviewed
        rating.save()
        item_reviewed.aggregate_rating.add_rating(rating)
        return ControllerResponse(status_text='Rated', obj=item_reviewed.aggregate_rating)
