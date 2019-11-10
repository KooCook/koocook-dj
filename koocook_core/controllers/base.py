from django.contrib.auth.models import User
from django.db.models import Model
from typing import Type

from ..models.base import ModelEncoder


class ControllerResponse:
    def __init__(self, status_text: str, obj: object):
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
        super().__init__('Unauthorised', None)


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
    def update(self):
        pass

    def retrieve_one(self):
        pass

    def retrieve_all(self):
        pass

    def delete(self):
        pass


class JsonRequestHandler:
    STATUS_CODE_MAP = {
        ControllerResponse: 200,
        ControllerResponseUnauthorised: 401,
    }

    def get_status_code(self, response: ControllerResponse):
        return self.STATUS_CODE_MAP[type(response)]

    def handle(self):
        from django.http import JsonResponse
        res = ControllerResponse()

        return JsonResponse(res.as_json(), status=self.get_status_code(res))
