import datetime
import json
import warnings

from koocook_core import models
import koocook_core.support as support
from django.core.exceptions import ObjectDoesNotExist  # for .get()
from koocook.settings.dirs import BASE_DIR
from koocook_core.support import utils

try:
    import datatrans.utils
    from datatrans import fooddata
    from datatrans.fooddata.search import *
    from datatrans.fooddata.detail import *
except ModuleNotFoundError:
    pass


def main():
    ignored_category = (
        FoodCategoryInstance.RESTAURANT_FOODS.value,
        FoodCategoryInstance.MEALS_ENTREES_AND_SIDE_DISHES.value,
        FoodCategoryInstance.BABY_FOODS.value,
        FoodCategoryInstance.SOUPS_SAUCES_AND_GRAVIES.value,
        FoodCategoryInstance.FAST_FOODS.value,
        FoodCategoryInstance.SNACKS.value,  # Could be used, but ignore for now
        FoodCategoryInstance.FAST_FOODS.value,
    )

    for i in range(1, 2):
        criteria = fooddata.search.FoodSearchCriteria(
            general_search_input='',
            included_data_types={FoodDataType.LEGACY: True},
            page_number=i
        )
        search_res = fooddata.api.send_food_search_api_request(criteria)
        search_res = fooddata.search.response.FoodSearchResponse(search_res)
        for food in search_res.foods:
            if food.data_type is not FoodDataType.LEGACY:
                continue
            detail_res = fooddata.api.send_food_detail_api_request(food.fdc_id)
            detail_res = fooddata.detail.response.FoodDetailResponse(detail_res, data_type=FoodDataType.LEGACY)
            food_: fooddata.detail.SrLegacyFood = detail_res.food
            if food_.food_category in ignored_category:
                continue
            nutrients = []
            for n in food_.food_nutrients:
                if n.amount:
                    unit_ = support.get_unit(n.nutrient.unit_name)
                    nutrients.append(
                        {
                            'nutrient': n.nutrient.name,
                            'quantity': support.Quantity(n.amount, unit_).get_db_str()
                        }
                    )

            name = food_.description
            if food_.common_names:
                name = food_.common_names
            m = models.MetaIngredient(name=name, nutrients=nutrients)
            m.save()
            print('saved ', m)
    pass
