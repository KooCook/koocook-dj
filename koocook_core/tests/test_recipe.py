from koocook_core.models.base import ModelEncoder
from django.test import RequestFactory
from django.db.models import QuerySet
from koocook_core.tests.base import AuthTestCase, create_dummy_recipe, create_dummy_recipe_body
from django.test import TestCase, RequestFactory
from .base import create_dummy_recipe, AuthTestCase
from koocook_core.models.recipe import Recipe, RecipeVisit, get_client_ip
from django.shortcuts import reverse
import json
from datetime import timedelta


class RecipeTests(AuthTestCase):
    BLANK_QS = QuerySet(model=Recipe)

    def test_total_time_with_prep_cook_time_are_second(self):
        time = timedelta(seconds=30)
        recipe = Recipe(prep_time=time, cook_time=time)
        self.assertEqual(recipe.total_time, timedelta(minutes=1))

    def test_total_time_with_prep_time_cook_time(self):
        time = timedelta(seconds=30)
        recipe = Recipe(prep_time=time, cook_time=time)
        self.assertEqual(recipe.total_time, timedelta(minutes=1))

    def test_total_time_without_prep_time(self):
        recipe = Recipe(cook_time=timedelta(seconds=90))
        self.assertEqual(recipe.total_time, timedelta(seconds=90))

    def test_total_time_without_cook_time(self):
        recipe = Recipe(prep_time=timedelta(seconds=90))
        self.assertEqual(recipe.total_time, timedelta(seconds=90))

    def test_total_time_without_prep_time_and_cook_time(self):
        recipe = Recipe()
        self.assertIsNone(recipe.total_time)

    def test_recipe_ingredient(self):
        recipe = Recipe()
        self.assertEqual(list(recipe.recipe_ingredients),
                         list(recipe.recipeingredient_set.all()))

    def test_recipe_method_not_allowed(self):
        response = self.client.patch(
            reverse("koocook_core:recipes:detail", kwargs={'recipe_id': 1}))
        self.assertEqual(response.status_code, 405)

    def test_unit_conversion(self):
        response = self.client.get(reverse("koocook_core:recipes:unit-conv"))
        with self.subTest("Get all conversion"):
            self.assertEqual(200, response.status_code)
        response = self.client.post(reverse("koocook_core:recipes:unit-conv"),
                                    {'value': 0, 'type': 'temperatureUnit',
                                     'base_unit': '°C', 'quote_unit': 'K'})
        with self.subTest("0 °C to Kelvin"):
            self.assertEqual(273.15, json.loads(response.content)['current'])

    def test_recipe_create_view(self):
        with self.subTest("Authenticated user access"):
            response = self.client.get(reverse("koocook_core:recipes:create"))
            self.assertTemplateUsed(response, "recipes/create.html")
        with self.subTest("Unauthenticated user access"):
            self.client.logout()
            response = self.client.get(reverse("koocook_core:recipes:create"))
            self.assertRedirects(response,
                                 f"{reverse('social:begin', args=['google-oauth2'])}?next={reverse('koocook_core:recipes:create')}",
                                 target_status_code=302)

    def test_recipe_detail_view_context(self):
        recipe = create_dummy_recipe(self.author)
        response = self.client.get(
            reverse("koocook_core:recipes:detail", kwargs={'recipe_id': recipe.id}))
        self.assertEqual(response.context["ingredients"], [])

    def test_recipe_update_view(self):
        recipe = create_dummy_recipe(self.author)
        response = self.client.get(
            reverse("koocook_core:recipes:edit", kwargs={'pk': recipe.id}))

        with self.subTest("Empty ingredients"):
            self.assertEqual(response.context["ingredients"], '[]')

        with self.subTest("Empty tags"):
            self.assertEqual(response.context["tags"], '[]')

        recipe_body = create_dummy_recipe_body(self.author)
        recipe_body.update(
            {'cookware_list': '[{"name": "Whisk"}, {"name": "Spatula"}]'})
        recipe_body.update(
            {'tags': '[{"name": "dummyTag", "label": {"name": "dummyLabel"}}]'})
        recipe_body.update(
            {'ingredients': '[{"quantity": {"number": "5", "unit": "tbsp"}, "name": "Pepper"}]'})
        recipe_body.update(
            {'recipe_instructions': '{}'})
        self.client.post(reverse("koocook_core:recipes:edit", kwargs={'pk': recipe.id}),
                         recipe_body)
        response = self.client.get(
            reverse("koocook_core:recipes:edit", kwargs={'pk': recipe.id}))

        with self.subTest("Posting a normal recipe with tags, cookware, and ingredients"):
            self.assertEqual(response.context["object"].name, 'dummy')
            self.assertListEqual(list(recipe.tag_set.all()),
                                 list(response.context["object"].tag_set.all()))
            self.assertEqual("Spatula", list(
                response.context["object"].equipment_set.all())[0].name)
            self.assertListEqual(list(recipe.recipe_ingredients),
                                 list(response.context["object"].recipe_ingredients))

        with self.subTest("Editing ingredients and tags"):
            ingredients = json.loads(response.context["ingredients"])
            tags = list(response.context["object"].tag_set.all())
            tags[0].name = "dummyTag2"
            recipe_body['tags'] = json.dumps(tags,
                                             cls=ModelEncoder)
            recipe_body['ingredients'] = json.dumps([{
                "id": ingredients[0]["id"],
                "quantity": {
                    "number": "3",
                    "unit": "tsp"
                },
                "name": "Salt"
            }])
            self.client.post(reverse("koocook_core:recipes:edit", kwargs={'pk': recipe.id}),
                             recipe_body)
            response = self.client.get(
                reverse("koocook_core:recipes:edit", kwargs={'pk': recipe.id}))
            self.assertEqual(
                'Salt', response.context["object"].recipe_ingredients[0].meta.name)

        self.client.login(username=self.user2.username, password=self.password)
        with self.subTest("Posting with a different user"):
            response = self.client.post(reverse("koocook_core:recipes:edit", kwargs={'pk': recipe.id}),
                                        recipe_body)
            self.assertEqual(response.status_code, 403)

    def test_delete_recipe(self):
        recipe = create_dummy_recipe(self.author)
        response = self.client.delete(reverse("koocook_core:recipes:detail", kwargs={
                                      'recipe_id': recipe.id}), recipe)
        with self.subTest():
            self.assertEqual(response.status_code, 200)
            with self.assertRaises(Recipe.DoesNotExist):
                Recipe.objects.get(pk=recipe.id)

        recipe = create_dummy_recipe(self.author)
        self.client.login(username=self.user2.username, password=self.password)
        response = self.client.delete(reverse("koocook_core:recipes:detail", kwargs={
                                      'recipe_id': recipe.id}), recipe)
        with self.subTest("That a non-author deletes the recipe should return a forbidden code"):
            self.assertEqual(response.status_code, 403)

    def test_recipe_user_listview(self):
        response = self.client.get(reverse("koocook_core:recipes:user"))
        with self.subTest("User has no recipes"):
            self.assertEqual(list(response.context["user_recipes"]), [])
        recipe = create_dummy_recipe(self.author)
        response = self.client.get(reverse("koocook_core:recipes:user"))
        with self.subTest("Checking status code"):
            self.assertEqual(response.status_code, 200)

        with self.subTest("User has a recipe"):
            self.assertEqual(response.context["user_recipes"][0].id, recipe.id)

    def test_recipe_preferred(self):
        response = self.client.get(reverse("koocook_core:recipes:suggested"))
        with self.subTest("Empty tag_set"):
            self.assertQuerysetEqual(
                self.BLANK_QS, response.context["tag_set"])

    def test_recipe_tags(self):
        response = self.client.get(
            reverse("koocook_core:recipes:tags"), {'name': ''})
        self.assertEqual(response.json()["current"], [])

    def test_recipe_search_listview(self):
        response = self.client.get(reverse("koocook_core:search"))

        with self.subTest("Search view must display all recipes with no filters"):
            self.assertQuerysetEqual(
                self.BLANK_QS, response.context["object_list"].all())

        recipe = create_dummy_recipe(self.author)
        response = self.client.get(
            reverse("koocook_core:search"), {'kw': recipe.name})
        with self.subTest("Search view must display recipes containing search keywords"):
            self.assertEqual(response.context["object_list"].all()[
                             0].name, recipe.name)

        response = self.client.get(
            reverse("koocook_core:search"), {'popular': 'true'})
        self.client.get(reverse("koocook_core:recipes:detail",
                                kwargs={'recipe_id': recipe.id}))
        with self.subTest("Search by popularity alone"):
            self.assertEqual(response.context["object_list"][0].view_count, 1)

        # response = self.client.get(reverse("koocook_core:search"), {'name_asc': '1'})
        # self.client.get(reverse("koocook_core:recipes:detail", kwargs={'recipe_id': recipe.id}))
        # with self.subTest("Sort by name"):
        #     self.assertEqual(response.context["object_list"][0].id, recipe.id)

        response = self.client.get(
            reverse("koocook_core:search") + '?order=athinmajig')
        with self.subTest("Sort by non-existent field"):
            self.assertEqual(response.context["object_list"][0].id, recipe.id)

        response = self.client.get(
            reverse("koocook_core:search") + '?order=name')
        with self.subTest("Sort by name"):
            self.assertEqual(response.context["object_list"][0].id, recipe.id)

        response = self.client.get(
            reverse("koocook_core:search") + '?order=name&ordering=desc')
        with self.subTest("Sort by name in descending order"):
            self.assertEqual(response.context["object_list"][0].id, recipe.id)

        response = self.client.get(
            reverse("koocook_core:search") + '?ingredients=Pepper')
        with self.subTest("Search by ingredient"):
            self.assertQuerysetEqual(
                self.BLANK_QS, response.context["object_list"].all())

        response = self.client.get(
            reverse("koocook_core:search") + '?cookware=Athinmajig')
        with self.subTest("Search by cookware"):
            self.assertQuerysetEqual(
                self.BLANK_QS, response.context["object_list"].all())


class RecipeVisitTest(AuthTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.recipe = create_dummy_recipe(self.author)
        self.visit = RecipeVisit.associate_recipe_with_user(
            self.kc_user, self.recipe)

    def test_unauthenticated_view(self):
        self.client.logout()
        response = self.client.get(
            reverse("koocook_core:recipes:detail", kwargs={'recipe_id': self.recipe.id}))
        with self.subTest():
            self.assertEqual(response.context["object"].view_count, 2)
        response = self.client.get(
            reverse("koocook_core:recipes:detail", kwargs={'recipe_id': self.recipe.id}))
        with self.subTest():
            self.assertEqual(response.context["object"].view_count, 2)

    def test_visit_count(self):
        with self.subTest():
            self.assertEqual(1, RecipeVisit.objects.all().count())
        self.recipe.delete()
        with self.subTest():
            self.assertEqual(0, RecipeVisit.objects.all().count())

    def test_visit_count_of_kc_user(self):
        with self.subTest():
            self.assertEqual(1, RecipeVisit.objects.all().count())

    def test_associate_recipe_visit_with_user(self):
        visit = RecipeVisit.associate_recipe_with_user(
            self.kc_user, self.recipe)
        with self.subTest():
            self.assertEqual(1, RecipeVisit.objects.all().count())

        with self.subTest("Getting the view count of a recipe"):
            self.assertEqual(self.recipe.recipevisit_set.all()[0], self.visit)
            self.assertEqual(1, self.recipe.view_count)

    def test_associate_recipe_visit_with_ip_address(self):
        self.request = RequestFactory()
        self.request = self.request.get('/')
        with self.subTest():
            self.assertEqual(get_client_ip(self.request),
                             self.request.META.get('REMOTE_ADDR'))

        visit = RecipeVisit.associate_recipe_with_ip_address(
            self.request, self.recipe)
        with self.subTest():
            self.assertEqual(visit.ip_address,
                             self.request.META.get('REMOTE_ADDR'))
            self.assertEqual(2, RecipeVisit.objects.all().count())
