import logging
from typing import Type
from django.db.models import Model

from .base import BaseController, ControllerResponse, ControllerResponseForbidden
from .decorators import apply_author_from_session
from .mixins import AuthorControllerMixin
from ..models import Rating, Comment, Recipe, Post

LOGGER = logging.getLogger(__name__)


class RatableController(AuthorControllerMixin, BaseController):
    item_reviewed_field = 'reviewed_item'

    def __init__(self, model: Type[Model], request_fields: dict):
        super().__init__(model, request_fields)

    @apply_author_from_session
    def rate(self, pk: int):
        body = ''
        item_reviewed = self.model.objects.get(pk=pk)
        if self.author == item_reviewed.author:
            LOGGER.info(f"{self.author.name} has attempted to rate his {self.item_reviewed_field} #{item_reviewed.id}. "
                        f"Nice try, but the operation has been rejected!")
            return ControllerResponseForbidden()
        rating_score = int(self.request_fields['rating_score'])
        rating_fields = {'author': self.request_fields['author']}
        if self.model == Comment:
            rating_fields['reviewed_comment'] = item_reviewed
            body = item_reviewed.id
        elif self.model == Recipe:
            rating_fields['reviewed_recipe'] = item_reviewed
            body = item_reviewed.name
        elif self.model == Post:
            rating_fields['reviewed_post'] = item_reviewed
            body = item_reviewed.id
        try:
            rating = Rating.objects.get(**rating_fields)
            rating.old_rating_value = rating.rating_value
        except Rating.DoesNotExist:
            rating = Rating(**rating_fields)
        rating.rating_value = rating_score
        rating.save()
        if body:
            LOGGER.info(f"{self.author.name} has rated {self.item_reviewed_field}#{item_reviewed.id} {body} for {rating_score}")
        item_reviewed.aggregate_rating.add_rating(rating, update=hasattr(rating, 'old_rating_value'))
        return ControllerResponse(status_text='Rated', obj=item_reviewed.aggregate_rating)
