from koocook_core.models.nutrition import RecipeIngredient, MetaIngredient
from koocook_core.tests.base import AuthTestCase, create_dummy_recipe, create_dummy_meta_ingredient


class NutritionTest(AuthTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.recipe = create_dummy_recipe(self.author)
        self.ingredient = create_dummy_meta_ingredient()
        RecipeIngredient.objects.create(quantity="3 kg", meta=self.ingredient, recipe=self.recipe)

    def test_many_quantity_of_ingredient(self):
        self.assertEqual(RecipeIngredient.objects.get(quantity="3 kg").nutrition,
                         [{"nutrient": "Carbohydrate", "quantity": '300.0 grams'},
                          {"nutrient": "Energy", "quantity": '900.0 kilocalories'},
                          {"nutrient": "Sugars", "quantity": '0.3 kilograms'}]
                         )

    def test_one_quantity_of_ingredient(self):
        ingredient = MetaIngredient.objects.create(name='testing',
                                                   nutrient=[{"nutrient": "Sugars",
                                                               "quantity": "0.5 kg"}])
        RecipeIngredient.objects.create(quantity='1 kg', meta=ingredient, recipe=self.recipe)
        self.assertEqual(RecipeIngredient.objects.get(quantity='1 kg').nutrition,
                         [{"nutrient": "Sugars", "quantity": '0.5 kilograms'}]
                         )

    def test_same_nutrient(self):
        ingredient = MetaIngredient.objects.create(name='testing!',
                                                   nutrient=[{"nutrient": "Sugars",
                                                               "quantity": "0.5 g"},
                                                              {"nutrient": "Sugars",
                                                               "quantity": "0.5 g"}
                                                              ])
        RecipeIngredient.objects.create(quantity='1 g', meta=ingredient, recipe=self.recipe)
        self.assertEqual(RecipeIngredient.objects.get(quantity='1 g').nutrition,
                         [{"nutrient": "Sugars", "quantity": '1.0 gram'}]
                         )

    def test_create_nutrient_without_bracket(self):
        ingredient = MetaIngredient.objects.create(name='testing!!',
                                                   nutrient=[{"nutrient": "Sugars",
                                                             "quantity": "0.1 g"}])
        RecipeIngredient.objects.create(quantity='1 gram', meta=ingredient, recipe=self.recipe)
        self.assertEqual(RecipeIngredient.objects.get(quantity='1 gram').nutrition,
                         [{"nutrient": "Sugars", "quantity": '0.1 grams'}]
                         )

    def test_recipe_nutrition(self):
        meta_ing_id = self.recipe.recipe_ingredients[0].meta.id
        self.assertEqual(self.recipe.nutrition,
                         [{"nutrient": "Carbohydrate", "quantity": '300.0 grams',
                           'sources': [{'name': 'test', 'quantity': '300.0 grams', 'id': meta_ing_id}]},
                          {"nutrient": "Energy", "quantity": '900.0 kilocalories',
                           'sources': [{'name': 'test', 'quantity': '900.0 kilocalories', 'id': meta_ing_id}]},
                          {"nutrient": "Sugars", "quantity": '0.3 kilograms',
                           'sources': [{'name': 'test', 'quantity': '0.3 kilograms', 'id': meta_ing_id}]}])

    def test_nutrition_with_many_ingredients(self):
        ingredient1 = MetaIngredient.objects.create(name='ingredient1',
                                                    nutrient=[{"nutrient": "Fat",
                                                              "quantity": "1 g"}])
        RecipeIngredient.objects.create(quantity='1 gram', meta=ingredient1, recipe=self.recipe)
        ingredient2 = MetaIngredient.objects.create(name='ingredient2',
                                                    nutrient=[{"nutrient": "Sugars",
                                                                "quantity": "1 g"},
                                                               {"nutrient": "Sugars",
                                                                "quantity": "1 g"},
                                                               {"nutrient": "Fiber",
                                                                "quantity": "5 g"}
                                                               ])
        RecipeIngredient.objects.create(quantity='1 g', meta=ingredient2, recipe=self.recipe)
        meta_ing_id_0 = self.recipe.recipe_ingredients[0].meta.id
        meta_ing_id_1 = ingredient1.id
        meta_ing_id_2 = ingredient2.id
        self.assertEqual(self.recipe.nutrition,
                         [{"nutrient": "Carbohydrate", "quantity": '300.0 grams',
                           'sources': [{'name': 'test', 'quantity': '300.0 grams', 'id': meta_ing_id_0}]},
                          {"nutrient": "Energy", "quantity": '900.0 kilocalories',
                           'sources': [{'name': 'test', 'quantity': '900.0 kilocalories', 'id': meta_ing_id_0}]},
                          {"nutrient": "Sugars", "quantity": '0.302 kilograms',
                           'sources': [{'name': 'test', 'quantity': '0.3 kilograms', 'relative': 99,
                                        'id': meta_ing_id_0},
                                       {'name': 'ingredient2', 'quantity': '2.0 grams', 'relative': 0,
                                        'id': meta_ing_id_2}]},
                          {"nutrient": "Fat", "quantity": '1.0 gram',
                           'sources': [{'name': 'ingredient1', 'quantity': '1.0 gram', 'id': meta_ing_id_1}]},
                          {"nutrient": "Fiber", "quantity": '5.0 grams',
                           'sources': [{'name': 'ingredient2', 'quantity': '5.0 grams', 'id': meta_ing_id_2}]}
                          ]
                         )
