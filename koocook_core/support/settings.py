from json import dumps, loads, JSONEncoder
from koocook_core.widgets import RecipeTagInput
from django.forms.widgets import Widget, CheckboxInput, Textarea, TextInput, HiddenInput
from enum import Enum
from typing import Type, Any


def str_to_bool(s: str) -> bool:
    s = s.lower()
    if s == 'true':
        return True
    elif s == 'false':
        return False
    raise ValueError


class PreferenceEnum(Enum):
    def __init__(self, key, val_type: Type = None, default=None, full_name: str = '', widget: Widget = None):
        self.key = key
        self.val_type = val_type
        self._default = default
        self._setting = self.default
        self.full_name = full_name
        self.widget = widget

    def __new__(cls, key, *args):
        obj = object.__new__(cls)
        obj._value_ = key
        return obj

    @property
    def default(self):
        return self._default

    @property
    def dict(self):
        return {self.key: self.default}


class Preference:
    """
        Preferences for users
        The settings can be retrieved using .get() in PreferenceManager
                                      and key name as the parameter
    """
    name: str = 'preference'
    widget: Widget = None
    val_type: Type = None

    def __init__(self, key='foo', val='bar', val_type: Type = str, full_name: str = '',
                 widget: Widget = None):
        self.name = key
        self.val_type = val_type
        self.setting = val
        if full_name is '':
            self.full_name = self.name
        else:
            self.full_name = full_name
        if widget is None:
            self.widget = self.build_widget_from_val_type()
        else:
            self.widget = widget

    def build_widget_from_val_type(self) -> Widget:
        attrs = {'v-model': 'preferences.' + self.name}
        if self.val_type is bool:
            return CheckboxInput(attrs=attrs)
        elif self.val_type is list:
            attrs.update({'class': 'textarea'})
            return Textarea(attrs=attrs)
        else:
            attrs.update({'class': 'input'})
            return TextInput(attrs=attrs)

    @classmethod
    def from_enum(cls, enum: PreferenceEnum):
        return cls(enum.key, enum.default,
                   enum.val_type, enum.full_name, widget=enum.widget)

    @property
    def setting(self):
        return self.to_python(self._setting)

    def to_python(self, value):
        if isinstance(value, self.val_type):
            return value
        elif hasattr(self.val_type, '__cast__'):
            return self.val_type.__cast__(value)
        elif self.val_type is bool:
            return str_to_bool(value)
        elif self.val_type is dict or self.val_type is list:
            return loads(value)
        else:
            return self.val_type(value)

    @setting.setter
    def setting(self, value):
        self._setting = self.to_python(value)

    def get_setting_str(self):
        return str(self.setting)

    @property
    def rendered(self):
        return self.widget.render(self.name, self.setting)

    @property
    def dict(self):
        return {self.name: self.get_setting_str()}


class TaggingPreference(PreferenceEnum):
    PREFERRED_TAGS = 'preferred_tags', list, [], "Preferred tags", \
                     RecipeTagInput(model='tags')


# class PrefEncoder(JSONEncoder):
#
#     def default(self, obj):
#         if hasattr(obj, 'as_dict'):
#             return obj.as_dict()
#         else:
#             if hasattr(obj, 'dict'):
#                 return obj.dict
#             else:
#                 return obj.__dict__


Preferences = (TaggingPreference,)


class PreferenceManager:
    def __init__(self):
        self.preferences = {}
        self.serialised_preferences = {}
        self.register_default_preferences()

    @classmethod
    def from_koocook_user(cls, user):
        from ..models import KoocookUser
        user: KoocookUser = user
        if type(user.preferences) is str:
            pref_dict = loads(user.preferences)
        else:
            pref_dict = user.preferences
        obj = cls()
        obj.preferences.update(pref_dict)
        import copy
        obj.serialised_preferences = pref_dict
        return obj

    def update_from_dict(self, pref_dict: dict):
        self.preferences.update(pref_dict)
        self.serialised_preferences.update(pref_dict)

    def update_from_json(self, json_str: str):
        self.update_from_dict(loads(json_str))

    def register_default_preferences(self):
        for section in Preferences:
            for pref in section:
                self.preferences.update(Preference.from_enum(pref).dict)

    def register_preference(self, preference: Preference):
        self.preferences.update(preference.dict)

    def all(self) -> list:
        prefs = []
        for pref_name in self.preferences:
            pref = to_preference(pref_name, self.preferences[pref_name])
            prefs.append(pref)
        return prefs

    @property
    def json(self):
        return dumps(self.preferences)

    def get(self, name: str) -> Any:
        """Returns a setting in the form of its type corresponding to the given key
        Args:
            name: A preference key

        Returns:
            (Any) The preference setting of the given key
        """
        return self.get_full(name)

    def get_full(self, name: str):
        return to_preference(name, self.preferences[name])

    def __setitem__(self, key, value):
        if type(value) is str:
            pref = to_preference(key, value)
        else:
            pref = Preference(key, value, type(value))
        self.register_preference(pref)
        self.serialised_preferences.update(pref.dict)

    def __getitem__(self, key):
        return self.get(key)


def get_section(pref_key) -> Preference:
    if isinstance(pref_key, Preference):
        return pref_key
    else:
        for pref in Preferences:
            try:
                return pref(pref_key)
            except ValueError:
                pass
        else:
            raise ValueError('\'{}\' is not a valid Preference'.format(pref_key))


def to_preference(key: str, value: str = ''):
    try:
        section = get_section(key)
    except ValueError:
        return None
    obj = Preference(section.key, section.default,
                     section.val_type, section.full_name,
                     section.widget)
    if value == '':
        return obj
    else:
        obj.setting = value
        return obj

