import logging
from typing import Type

from .base import BaseController, ControllerResponse
from .decorators import apply_author_from_session
from ..models import Author, Comment
from ..models.base import SerialisableModel


LOGGER = logging.getLogger(__name__)


class AuthorControllerMixin(BaseController):
    @property
    def author(self) -> Author:
        return self.request_fields['author']


class CommentControllerMixin(AuthorControllerMixin):
    item_reviewed_field: str = "reviewed_item"
    comment_model: Type[SerialisableModel] = Comment

    def get_all_comments_of_item_id(self, *args, item_id: int):
        all_comments = list(self.model.objects.get(pk=item_id).comment_set.all())
        return ControllerResponse("Retrieved all comments", obj=all_comments)

    @apply_author_from_session
    def comment(self, item_id: int) -> ControllerResponse:
        assert self.item_reviewed_field != "reviewed_item"  # Reviewed item not set"
        comment_fields = {field: val for (field, val) in self.request_fields.items()
                          if field in Comment.field_names()}
        comment_fields['author'] = self.author
        comment_fields.update({self.item_reviewed_field: self.model.objects.get(pk=item_id)})
        comment = self.comment_model(**comment_fields)
        comment.save()
        LOGGER.info(f"{self.author.name} has commented on {self.item_reviewed_field}#{item_id} [ID #{comment.id}]")
        comment = Comment.objects.get(pk=comment.id)
        return ControllerResponse(status_text='Retrieved', obj=comment)
