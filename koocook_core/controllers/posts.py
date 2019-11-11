# Single view w/ Ajax
from django.db.models import Model
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse, QueryDict

from .base import BaseController, BaseHandler, ControllerResponse, ControllerResponseUnauthorised
from ..models import Post, Author
from ..views import GuestPostStreamView, UserPostStreamView


def apply_author_from_session(func):
    def wrapper(controller, *args, **kwargs):
        try:
            controller.request_fields['author'] = Author.from_dj_user(controller.request.user)
        except Author.DoesNotExist:
            return ControllerResponseUnauthorised()

        if (len(args) > 0 and args[0] is not None) or len(kwargs) > 0:
            return func(controller, *args, **kwargs)
        else:
            return func(controller)
    return wrapper


class PostController(BaseController):

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
    def update_post(self, request: HttpRequest, post_id: int) -> JsonResponse:
        found = self.find_by_id(post_id)
        if found.author != request.author:
            return JsonResponse({'status': 'Forbidden'}, status=403)
        params = QueryDict(request.body).dict()
        updated_fields = list(set(params.keys()).intersection(set(self.model_field_names)))
        for field in updated_fields:
            setattr(found, field, params[field])
        found.save()
        return JsonResponse({'status': 'Post updated', 'post': found.as_json})

    @apply_author_from_session
    def delete_post(self, request: HttpRequest, post_id: int) -> JsonResponse:
        found = self.find_by_id(post_id)
        if found.author != request.author:
            return JsonResponse({'status': 'Forbidden'}, status=403)
        found.delete()
        return JsonResponse({'status': 'Post deleted'})

    def upsert_post(self, request: HttpRequest, post_id: int) -> JsonResponse:
        found, created = self.model.objects.get_or_create(pk=post_id)
        if not created:
            if found.author != request.author:
                return JsonResponse({'status': 'Forbidden'}, status=403)
            for field in self.model_field_names:
                setattr(found, field, request.POST.get(field))
            found.save()
            return JsonResponse({'status': 'Post updated'})
        else:
            return JsonResponse({'status': 'Post created'})


class PostHandler(BaseHandler):
    def __init__(self):
        super().__init__(PostController.default())
        self.handler_map = {
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

