from koocook_core.controllers.base import ControllerResponse, JsonRequestHandler
from koocook_core.controllers.mixins import CommentControllerMixin
from koocook_core.controllers.rating import RatableController
from koocook_core.models import Recipe
from koocook_core.support import units, get_unit, TemperatureUnit, SpecialUnit


class RecipeController(RatableController, CommentControllerMixin):
    item_reviewed_field = 'reviewed_recipe'

    def __init__(self):
        super().__init__(Recipe, {})

    def get_unit_conversion_table(self, section='all'):
        table = {}
        for unit_section in units:
            for unit in unit_section:
                if not unit.type in table:
                    table[unit.type] = []
                if not section == 'serving' and unit.as_dict()['value']:
                    table[unit.type].append(get_unit(unit))
                else:
                    if unit_section is SpecialUnit:
                        table[unit.type].append(get_unit(unit))
        return ControllerResponse("Retrieved", obj=table)

    def determine_section(self):
        if 'section' in self.request_fields:
            resp = self.get_unit_conversion_table(section=self.request_fields['section'])
            return resp
        else:
            return self.convert()

    def convert(self):
        try:
            if 'value' not in self.request_fields:
                return ControllerResponse("None")
            value = float(self.request_fields["value"])
            type = self.request_fields["type"]
            base = self.request_fields["base_unit"]
            dest = self.request_fields["dest_unit"]
            if type == 'temperatureUnit':
                return ControllerResponse("Converted", obj=TemperatureUnit.convert(value, base, dest))
            else:
                return ControllerResponse("None")
        except ValueError:
            return ControllerResponse("None")

    @classmethod
    def default(cls):
        return cls()


class RecipeAPIHandler(JsonRequestHandler):
    def __init__(self):
        super().__init__(RecipeController.default())
        self.handler_map = {
            'unit_conv': {
                'GET': 'get_unit_conversion_table',
                'POST': 'determine_section'
            },
            'comment': {
                'GET': 'get_all_comments_of_item_id',
                'POST': 'comment'
            },
            'rate': {
                'POST': 'rate'
            }
        }

    @classmethod
    def instance(cls):
        return cls()
