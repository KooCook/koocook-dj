import html2markdown
import html
from markdown import markdown
from django.db import models


class MarkdownSource:
    def __init__(self, source: str):
        self.source = source
        self.sanitise()

    @property
    def rendered(self):
        return self.render_html()

    def sanitise(self):
        self.source = html2markdown.convert(self.source)
        self.source = html.escape(self.source).replace("&amp;", "&")

    def render_html(self):
        return markdown(self.source, safe_mode='escape', extensions=['fenced_code'])

    def get_db_str(self):
        return self.source

    def __str__(self):
        return self.source

    # Monkey patched
    def __len__(self):
        return len(str(self))


class FormattedField(models.TextField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection):
        if value is None or value is '':
            return value
        return MarkdownSource(value)

    def to_python(self, value):
        if isinstance(value, MarkdownSource):
            return value

        if value is None:
            return value

        return MarkdownSource(value)

    def get_prep_value(self, value):
        if isinstance(value, MarkdownSource):
            return value.get_db_str()

        if value is None:
            return value
        return MarkdownSource(value).get_db_str()

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return self.get_prep_value(value)

