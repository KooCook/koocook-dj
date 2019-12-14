# Single view w/ Ajax
from django.http import HttpRequest, HttpResponse, JsonResponse

from .base import BaseHandler, ControllerResponse, ControllerResponseForbidden
from .decorators import apply_author_from_session
from .mixins import CommentControllerMixin
from .rating import RatableController
from ..models import Post, Author
from ..views import GuestPostStreamView, UserPostStreamView


class PostController(RatableController, CommentControllerMixin):
    item_reviewed_field = 'reviewed_post'

    def __init__(self):
        super().__init__(Post, {})

    @classmethod
    def default(cls):
        return cls()
    #
    # def get_model_request_fields(self, request: HttpRequest) -> dict:
    #     return {field_name: request.POST.get(field_name) for field_name in self.model_field_names}

    @apply_author_from_session
    def create(self) -> ControllerResponse:
        return super().create()

    def render_stream_view(self) -> HttpResponse:
        if self.request.user.is_authenticated:
            return UserPostStreamView.as_view()(self.request)
        else:
            return GuestPostStreamView.as_view()(self.request)

    @apply_author_from_session
    def retrieve_all(self) -> ControllerResponse:
        all_items = super().retrieve_all().obj
        for item in all_items:
            if item.author == self.author:
                item.hidden = True
        return ControllerResponse(status_text='Retrieved', obj=all_items)

    @apply_author_from_session
    def retrieve_all_for_user(self) -> ControllerResponse:
        """
        Retrieves all posts of the current user

            Returns:
                ControllerResponse: A response and its result in ControllerResponse class
        """
        return ControllerResponse(status_text='Retrieved', obj=list(self.model.objects.filter(author=self.author)))

    @apply_author_from_session
    def retrieve_all_from_following(self) -> ControllerResponse:
        authors = [user.author for user in self.author.user.following.all()]
        return ControllerResponse(status_text='Retrieved following', obj=list(self.model.objects.filter(author__in=authors)))

    @apply_author_from_session
    def update_post(self, pk: int) -> ControllerResponse:
        obj = self.find_by_id(pk)
        if obj.author == self.author:
            return super().update(obj)
        else:
            return ControllerResponseForbidden()

    @apply_author_from_session
    def delete_post(self, pk: int) -> ControllerResponse:
        obj = self.find_by_id(pk)
        if obj.author == self.author:
            return self.delete(obj)
        else:
            return ControllerResponseForbidden()

    # TODO: Needs more implementation on this
    # def upsert_post(self, request: HttpRequest, post_id: int) -> JsonResponse:
    #     found, created = self.model.objects.get_or_create(pk=post_id)
    #     if not created:
    #         if found.author != request.author:
    #             return JsonResponse({'status': 'Forbidden'}, status=403)
    #         for field in self.model_field_names:
    #             setattr(found, field, request.POST.get(field))
    #         found.save()
    #         return JsonResponse({'status': 'Post updated'})
    #     else:
    #         return JsonResponse({'status': 'Post created'})


class PostHandler(BaseHandler):
    def __init__(self):
        super().__init__(PostController.default())
        self.handler_map = {
            'comment': {
                'GET': 'get_all_comments_of_item_id',
                'POST': 'comment'
            },
            'rate': {
                'POST': 'rate'
            },
            'user': {
                'GET': 'retrieve_all_for_user'
            },
            'all': {
                'GET': 'retrieve_all'
            },
            'followee': {
                'GET': 'retrieve_all_from_following'
            },
            'GET': 'render_stream_view',
            'POST': 'create',
            # 'GET': None, Do we really need a single view of a post?
            'DELETE': 'delete_post',
            'PATCH': 'update_post'
        }

    @classmethod
    def instance(cls):
        return cls()
    #
    # def handle(self, request: HttpRequest, pk=None):
    #     func, arg_pk = self._get_handler_for_method(request.method)
    #     return func(request, pk) if arg_pk else func(request)
