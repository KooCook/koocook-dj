import json
from json import JSONEncoder
from django.db import models
from django.utils.html import mark_safe


class SerialisableModel:
    body = None
    include = ()
    exclude = ()

    # TODO: Process a Markdown text here
    @staticmethod
    def process_text_format(text: str, text_format: str = "md") -> str:
        if text_format == 'md':
            pass
        return mark_safe(text)

    @property
    def fields(self) -> list:
        return list(self.include) + [field.name for field in self._meta.fields]

    @property
    def as_dict(self) -> dict:
        dict_repr = {field: getattr(self, field) for field in self.fields
                     if field not in self.exclude}
        return dict_repr

    @property
    def as_json(self) -> str:
        return json.dumps(self.as_dict, cls=ModelEncoder)


class ModelEncoder(JSONEncoder):
    def default(self, obj: models.Model):
        if hasattr(obj, 'as_dict'):
            return obj.as_dict
        else:
            if isinstance(obj, models.Model):
                return {field.name: getattr(obj, field.name) for field in obj._meta.fields}
            else:
                return str(obj)
