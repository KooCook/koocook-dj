import json
from json import JSONEncoder

from django.db import models
from django.db.models import Field
from django.http import HttpRequest


def get_client_ip(request: HttpRequest):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')


def transform_to_field(key):
    field = Field(name=key)
    return field


class SerialisableModel:
    body = None
    include = ()
    exclude = ()

    @property
    def dict_fields(self) -> list:
        return [transform_to_field(include) for include in self.include if getattr(self, include)] + \
               [field for field in self._meta.fields]

    def as_dict(self) -> dict:
        return {field.name: getattr(self, field.name) for field in self.dict_fields
                if field.name not in self.exclude and hasattr(self, field.name)}

    def as_json(self) -> str:
        return json.dumps(self.as_dict, cls=ModelEncoder)


class ModelEncoder(JSONEncoder):
    def default(self, obj: models.Model):
        if hasattr(obj, 'as_dict'):
            return obj.as_dict()
        else:
            if isinstance(obj, models.Model):
                if isinstance(obj, SerialisableModel):
                    return {field.name: getattr(obj, field.name) for field in obj.dict_fields}
                else:
                    return {field.name: getattr(obj, field.name) for field in obj._meta.fields}
            else:
                if type(obj) in [int, float]:
                    return obj
                else:
                    return str(obj)
