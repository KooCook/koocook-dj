from django.contrib.auth.models import User
from django.db.models import Model
from django.http import JsonResponse, HttpRequest, HttpResponse, QueryDict
from typing import Type

from ..models.base import ModelEncoder


def user_only(func):
    def wrapper(controller, *args, **kwargs):
        if not controller.request_fields['user'].is_authenticated:
            return ControllerResponseUnauthorised()
        if (len(args) > 0 and args[0] is not None) or len(kwargs) > 0:
            return func(controller, *args, **kwargs)
        else:
            return func(controller)
    return wrapper


class ControllerResponse:
    def __init__(self, status_text: str, obj: object = None):
        self.status_text = status_text
        self.obj = obj

    def as_dict(self) -> dict:
        repr_dict = {'status': self.status_text}
        if self.obj:
            repr_dict['current'] = self.obj
        return repr_dict

    def as_json(self) -> str:
        import json
        return json.dumps(self.as_dict(), cls=ModelEncoder)


class ControllerResponseUnauthorised(ControllerResponse):
    def __init__(self):
        super().__init__('Unauthorised')


class ControllerResponseForbidden(ControllerResponse):
    def __init__(self):
        super().__init__('Forbidden')


class ControllerResponseNotAllowed(ControllerResponse):
    def __init__(self):
        super().__init__('Method Not Allowed')


class BaseController:
    def __init__(self, model: Type[Model], request_fields: dict):
        self.model = model
        self.request_fields = request_fields
        self.request_params = {}
        self.http_verb_map = {}

    @property
    def user(self) -> User:
        return self.request_fields['user']

    @classmethod
    def default(cls):
        return cls(Model, {})

    @property
    def model_field_names(self) -> list:
        return [field.name for field in self.model._meta.get_fields()]

    @property
    def model_request_fields(self) -> dict:
        return {field_name: self.request_fields[field_name] for field_name in self.model_field_names
                if field_name in self.request_fields}

    def find_by_id(self, model_id: int) -> Model:
        return self.model.objects.get(pk=model_id)

    @user_only
    def create(self) -> ControllerResponse:
        creation = self.model(**self.model_request_fields)
        creation.save()
        return ControllerResponse(status_text='Created', obj=creation)

    @user_only
    def update(self, found) -> ControllerResponse:
        # params = QueryDict(request.body).dict()
        updated_fields = list(set(self.request_fields.keys()).intersection(set(self.model_field_names)))
        for field in updated_fields:
            setattr(found, field, self.request_fields[field])
        print(self.request_fields)
        found.save()
        found = self.model.objects.get(pk=found.id)
        return ControllerResponse(status_text='Updated', obj=found)

    def retrieve_one(self) -> ControllerResponse:
        pass

    def retrieve_all(self) -> ControllerResponse:
        return ControllerResponse(status_text='Retrieved', obj=list(self.model.objects.all()))

    @user_only
    def delete(self, found) -> ControllerResponse:
        found.delete()
        return ControllerResponse(status_text='Deleted', obj=found)


class BaseHandler:
    STATUS_CODE_MAP = {
        ControllerResponse: 200,
        ControllerResponseUnauthorised: 401,
        ControllerResponseForbidden: 403,
        ControllerResponseNotAllowed: 405
    }

    def __init__(self, controller_type: BaseController):
        self.controller = controller_type
        self.handler_map = {}

    @classmethod
    def instance(cls):
        return cls(BaseController.default())

    def get_handler_for(self, request: HttpRequest, controller, alias):
        if not alias:
            return self._get_handler_for_method(controller, request.method, self.handler_map)
        sub_handler = self.handler_map[alias]
        if type(sub_handler) is str:
            if callable(getattr(controller, sub_handler)):
                return sub_handler
            raise ValueError
        elif type(sub_handler) is dict:
            return self._get_handler_for_method(controller, request.method, sub_handler)

    def _get_handler_for_method(self, controller, method, method_map):
        normalised_method = method.upper()
        if normalised_method in method_map:
            handler = method_map[normalised_method]
            return getattr(controller, handler)
        return ControllerResponseNotAllowed()

    def restore_controller(self, request: HttpRequest):
        controller = self.controller.default()
        if request.method not in ['GET', 'POST']:
            controller.request_fields.update(QueryDict(request.body).dict())
        else:
            controller.request_fields.update(request.POST.dict())
        controller.request_fields['user'] = request.user
        return controller

    def _internal_handle(self, request: HttpRequest, alias: str = None, **kwargs) -> ControllerResponse:
        controller = self.restore_controller(request)
        controller.request = request
        handler = self.get_handler_for(request, controller, alias)
        if len(kwargs) > 0:
            func = handler
            return func(request, **kwargs)
        else:
            func = handler
            if callable(func):
                return func()
            else:
                return func

    def get_status_code(self, response: ControllerResponse) -> int:
        return self.STATUS_CODE_MAP[type(response)]

    def handle(self, request: HttpRequest, alias: str = None, **kwargs) -> HttpResponse:
        res = self._internal_handle(request, alias, **kwargs)
        if hasattr(res, 'as_json'):
            return JsonResponse(res.as_dict(), status=self.get_status_code(res), encoder=ModelEncoder)
        else:
            return res


class JsonRequestHandler(BaseHandler):

    def handle(self, request: HttpRequest, alias: str = None, **kwargs) -> JsonResponse:
        res = self._internal_handle(request, alias, **kwargs)
        if hasattr(res, 'as_dict'):
            return JsonResponse(res.as_dict(), status=self.get_status_code(res), encoder=ModelEncoder)
        else:
            return res
