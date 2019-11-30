from typing import List


from datatrans import fooddata
from datatrans.fooddata.search import *


from koocook_core import support


def parse_food_nutrients(food_nutrients) -> List[dict]:
    nutrients = []
    for n in food_nutrients:
        if n.amount:
            unit_ = support.get_unit(n.nutrient.unit_name)
            nutrients.append(
                {
                    'nutrient': n.nutrient.name,
                    'quantity': support.Quantity(n.amount, unit_).get_db_str()
                }
            )
    return nutrients


def get_nutrients(ingr: str) -> (List[dict], str):
    """ Returns a list of nutrients given an ingredient name """
    res = fooddata.api.send_food_search_api_request(FoodSearchCriteria(
        general_search_input=ingr,
    ))
    res = fooddata.search.response.FoodSearchResponse(res)
    food = res.foods[0]
    res = fooddata.api.send_food_detail_api_request(fdc_id=food.fdc_id)
    res = fooddata.detail.response.FoodDetailResponse(res, data_type=food.data_type)
    return parse_food_nutrients(res.food.food_nutrients), res.food.description
