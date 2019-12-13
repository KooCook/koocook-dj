from koocook_core.widgets import RecipeTagInput
from koocook_auth.services import BasePreferenceManager, PreferenceEnum


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


class PreferenceManager(BasePreferenceManager):
    DEFINED_PREFERENCES = Preferences
