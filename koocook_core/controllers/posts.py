# Single view w/ Ajax
from django.db.models import Model
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, JsonResponse, QueryDict


from ..models import Post, Author
from ..views import GuestPostStreamView, UserPostStreamView


def apply_author_from_session(func):
    def wrapper(controller, request: HttpRequest, *args, **kwargs):
        try:
            request.author = Author.from_dj_user(request.user)
        except Author.DoesNotExist:
            return HttpResponseForbidden()

        if (len(args) > 0 and args[0] is not None) or len(kwargs) > 0:
            return func(controller, request, *args, **kwargs)
        else:
            return func(controller, request)
    return wrapper


class PostController:

    def __init__(self):
        self.model = Post

    @property
    def model_field_names(self) -> list:
        return [field.name for field in self.model._meta.get_fields()]

    def get_model_request_fields(self, request: HttpRequest) -> dict:
        return {field_name: request.POST.get(field_name) for field_name in self.model_field_names}

    def find_by_id(self, post_id: int) -> Post:
        return self.model.objects.get(pk=post_id)

    @apply_author_from_session
    def create_post(self, request: HttpRequest) -> JsonResponse:
        creation = self.model(**self.get_model_request_fields(request))
        creation.author = request.author
        creation.save()
        return JsonResponse({'status': 'Post created', 'post': creation.as_json})

    @staticmethod
    def render_stream_view(request: HttpRequest) -> HttpResponse:
        if request.user.is_authenticated:
            return UserPostStreamView.as_view()(request)
        else:
            return GuestPostStreamView.as_view()(request)

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
        found = self.find_by_id(found.id)
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


class BaseHandler:
    @staticmethod
    def _get_handler_for_method(handler_map: dict, method):
        if method.upper() in handler_map:
            return handler_map[method]
        else:
            raise NotImplementedError


class PostHandler(BaseHandler):
    def __init__(self):
        self.controller = PostController()
        self.plain_map = {
            'GET': (self.controller.render_stream_view, False),
            'POST': (self.controller.create_post, True),
            # 'GET': None, Do we really need a single view of a post?
            'DELETE': (self.controller.delete_post, True),
            'PATCH': (self.controller.update_post, True)}

    @classmethod
    def instance(cls):
        return cls()

    def handle(self, request: HttpRequest, pk=None):
        func, arg_pk = self._get_handler_for_method(self.plain_map, request.method)
        return func(request, pk) if arg_pk else func(request)

