from typing import Type
from django.db.models import Model

from .base import BaseController, ControllerResponse, ControllerResponseForbidden
from .decorators import apply_author_from_session
from .mixins import AuthorControllerMixin
from ..models import Rating, Comment, Recipe, Post


class RatableController(AuthorControllerMixin, BaseController):
    item_reviewed_field = 'reviewed_item'

    def __init__(self, model: Type[Model], request_fields: dict):
        super().__init__(model, request_fields)

    @apply_author_from_session
    def rate(self, pk: int):
        item_reviewed = self.model.objects.get(pk=pk)
        if self.author == item_reviewed.author:
            return ControllerResponseForbidden()
        rating_score = int(self.request_fields['rating_score'])
        rating_fields = {'author': self.request_fields['author']}
        if self.model == Comment:
            rating_fields['reviewed_comment'] = item_reviewed
        elif self.model == Recipe:
            rating_fields['reviewed_recipe'] = item_reviewed
        elif self.model == Post:
            rating_fields['reviewed_post'] = item_reviewed
        try:
            rating = Rating.objects.get(**rating_fields)
            rating.old_rating_value = rating.rating_value
        except Rating.DoesNotExist:
            rating = Rating(**rating_fields)
        rating.rating_value = rating_score
        rating.save()
        item_reviewed.aggregate_rating.add_rating(rating, update=hasattr(rating, 'old_rating_value'))
        return ControllerResponse(status_text='Rated', obj=item_reviewed.aggregate_rating)
