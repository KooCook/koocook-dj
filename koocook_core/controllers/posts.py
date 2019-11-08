# Single view w/ Ajax
from django.db.models import Model
from django.http import HttpRequest, JsonResponse


from ..models import Post


class PostController:

    def __init__(self):
        self.model = Post

    @property
    def model_field_names(self) -> list:
        return [field.name for field in self.model._meta.get_fields()]

    def get_model_request_fields(self, request: HttpRequest) -> dict:
        return {field_name: request.POST.get(field_name) for field_name in self.model_field_names}

    def find_by_id(self, post_id: int) -> Model:
        return self.model.objects.get(pk=post_id)

    def create_post(self, request: HttpRequest) -> JsonResponse:
        creation = self.model(**self.get_model_request_fields(request))
        creation.save()
        return JsonResponse({'status': 'Post created'})

    def retrieve_all_posts(self) -> list:
        return list(self.model.objects.all())

    def update_post(self, request: HttpRequest, post_id: int) -> JsonResponse:
        found = self.find_by_id(post_id)
        updated_fields = list(set(request.POST.keys()).intersection(set(self.model_field_names)))
        for field in updated_fields:
            setattr(found, field, request.POST.get(field))
        found.save()
        return JsonResponse({'status': 'Post updated'})

    def delete_post(self, request: HttpRequest, post_id: int) -> JsonResponse:
        found = self.find_by_id(post_id)
        found.delete()
        return JsonResponse({'status': 'Post deleted'})

    def upsert_post(self, request: HttpRequest, post_id: int) -> JsonResponse:
        found, created = self.model.objects.get_or_create(pk=post_id)
        if not created:
            for field in self.model_field_names:
                setattr(found, field, request.POST.get(field))
            found.save()
            return JsonResponse({'status': 'Post updated'})
        else:
            return JsonResponse({'status': 'Post created'})


class BaseHandler:
    @staticmethod
    def _get_handler_for_method(handler_map: dict, method):
        if method in handler_map:
            return handler_map[method]
        else:
            raise NotImplementedError


class PostHandler(BaseHandler):
    def __init__(self):
        self.controller = PostController()
        self.plain_map = {
            'GET': (self.controller.retrieve_all_posts, False),
            'POST': (self.controller.create_post, True)
        }
        self.single_id_map = { # 'GET': None, Do we really need a single view of a post?
            'DELETE': (self.controller.delete_post, True),
            'PATCH': (self.controller.update_post, True)}

    @classmethod
    def instance(cls):
        return cls()

    def handle(self, request: HttpRequest, pk=None):
        func, arg_pk = self._get_handler_for_method(self.single_id_map, request.method)
        return func(request, pk) if arg_pk else func(request)

