from django.contrib.auth.models import User
from django.db.models import Model
from django.http import JsonResponse, HttpRequest
from typing import Type

from ..models.base import ModelEncoder


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


def user_only(func):
    def wrapper(controller: BaseController, *args, **kwargs):
        if type(controller.request_fields['user']) == User:
            return ControllerResponseUnauthorised()
        if (len(args) > 0 and args[0] is not None) or len(kwargs) > 0:
            return func(controller, *args, **kwargs)
        else:
            return func(controller)
    return wrapper


class BaseController:
    def __init__(self, model: Type[Model], request_fields: dict):
        self.model = model
        self.request_fields = request_fields

    @classmethod
    def default(cls):
        return cls(Model, {})

    @property
    def model_field_names(self) -> list:
        return [field.name for field in self.model._meta.get_fields()]

    @property
    def model_request_fields(self) -> dict:
        return {field_name: self.request_fields[field_name] for field_name in self.model_field_names}

    def find_by_id(self, model_id: int) -> Model:
        return self.model.objects.get(pk=model_id)

    @user_only
    def create(self) -> ControllerResponse:
        creation = self.model(**self.model_request_fields)
        creation.save()
        return ControllerResponse(status_text='Created', obj=creation)

    @user_only
    def update(self) -> ControllerResponse:
        pass

    def retrieve_one(self) -> ControllerResponse:
        pass

    def retrieve_all(self) -> ControllerResponse:
        pass

    @user_only
    def delete(self) -> ControllerResponse:
        pass


class BaseHandler:

    def __init__(self, controller_type: BaseController):
        self.controller = controller_type
        self.handler_map = {}

    @classmethod
    def instance(cls):
        return cls(BaseController.default())

    def get_handler_for(self, request: HttpRequest, alias):
        if not alias:
            return self._get_handler_for_method(request.method)
        sub_handler = self.handler_map[alias]
        if callable(sub_handler):
            return sub_handler
        else:
            return self._get_handler_for_method(request.method)

    def _get_handler_for_method(self, method):
        if method.upper() in self.handler_map:
            return self.handler_map[method]
        raise NotImplementedError

    def restore_controller_fields(self, request: HttpRequest):
        self.controller = self.controller.default()
        self.controller.request_fields.update(request.POST.dict())
        self.controller.request_fields['user'] = request.user

    def handle(self, request: HttpRequest, alias: str = None) -> ControllerResponse:
        self.restore_controller_fields(request)
        handler = self.get_handler_for(request, alias)
        if type(handler) is tuple:
            func, args = handler
        else:
            func = handler
        return func(request)


class JsonRequestHandler(BaseHandler):
    STATUS_CODE_MAP = {
        ControllerResponse: 200,
        ControllerResponseUnauthorised: 401,
    }

    def get_status_code(self, response: ControllerResponse) -> int:
        return self.STATUS_CODE_MAP[type(response)]

    def handle(self, request: HttpRequest, alias: str = None) -> JsonResponse:
        res = super().handle(request, alias)
        return JsonResponse(res.as_json(), status=self.get_status_code(res))
