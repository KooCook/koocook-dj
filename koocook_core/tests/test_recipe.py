from datetime import timedelta
from django.shortcuts import reverse
from koocook_core.models.recipe import Recipe, RecipeVisit, get_client_ip
from .base import create_dummy_recipe, AuthTestCase
from django.test import TestCase, RequestFactory
from koocook_core.tests.base import AuthTestCase, create_dummy_recipe, create_dummy_recipe_body


class RecipeTests(AuthTestCase):
    def test_total_time_with_prep_cook_time_are_second(self):
        time = timedelta(seconds=30)
        recipe = Recipe(prep_time=time, cook_time=time)
        self.assertEqual(recipe.total_time, timedelta(minutes=1))

    def test_recipe_method_not_allowed(self):
        response = self.client.patch(reverse("koocook_core:recipe", kwargs={'recipe_id': 1}))
        self.assertEqual(response.status_code, 405)

    def test_recipe_create_view(self):
        with self.subTest("Authenticated user access"):
            response = self.client.get(reverse("koocook_core:recipe-create"))
            self.assertTemplateUsed(response, "recipes/create.html")
        with self.subTest("Unauthenticated user access"):
            self.client.logout()
            response = self.client.get(reverse("koocook_core:recipe-create"))
            self.assertRedirects(response,
                                 f"{reverse('social:begin', args=['google-oauth2'])}?next={reverse('koocook_core:recipe-create')}",
                                 target_status_code=302)

    def test_recipe_detail_view_context(self):
        recipe = create_dummy_recipe(self.author)
        response = self.client.get(reverse("koocook_core:recipe", kwargs={'recipe_id': recipe.id}))
        self.assertEqual(response.context["ingredients"], [])

    def test_recipe_update_view(self):
        recipe = create_dummy_recipe(self.author)
        response = self.client.get(reverse("koocook_core:recipe-edit", kwargs={'pk': recipe.id}))

        with self.subTest():
            self.assertEqual(response.context["ingredients"], '[]')

        with self.subTest():
            self.assertEqual(response.context["tags"], '[]')

        recipe_body = create_dummy_recipe_body(self.author)
        recipe_body.update({'tags': '[{"name": "dummyTag", "label": {"name": "dummyLabel"}}]'})
        recipe_body.update({'ingredients': '[]'})
        self.client.post(reverse("koocook_core:recipe-edit", kwargs={'pk': recipe.id}),
                         recipe_body)
        response = self.client.get(reverse("koocook_core:recipe-edit", kwargs={'pk': recipe.id}))

        with self.subTest("Posting a normal recipe"):
            self.assertEqual(response.context["object"].name, 'dummy')
            self.assertEqual(list(response.context["object"].recipe_ingredients), [])

        self.client.login(username=self.user2.username, password=self.password)
        with self.subTest("Posting with a different user"):
            response = self.client.post(reverse("koocook_core:recipe-edit", kwargs={'pk': recipe.id}),
                             recipe_body)
            self.assertEqual(response.status_code, 403)

    def test_delete_recipe(self):
        recipe = create_dummy_recipe(self.author)
        response = self.client.delete(reverse("koocook_core:recipe", kwargs={'recipe_id': recipe.id}), recipe)
        with self.subTest():
            self.assertEqual(response.status_code, 200)
            with self.assertRaises(Recipe.DoesNotExist):
                Recipe.objects.get(pk=recipe.id)

        recipe = create_dummy_recipe(self.author)
        self.client.login(username=self.user2.username, password=self.password)
        response = self.client.delete(reverse("koocook_core:recipe", kwargs={'recipe_id': recipe.id}), recipe)
        with self.subTest("That a non-author deletes the recipe should return a forbidden code"):
            self.assertEqual(response.status_code, 403)

    def test_recipe_user_listview(self):
        response = self.client.get(reverse("koocook_core:recipe-user"))
        with self.subTest("User has no recipes"):
            self.assertEqual(list(response.context["user_recipes"]), [])
        recipe = create_dummy_recipe(self.author)
        response = self.client.get(reverse("koocook_core:recipe-user"))
        with self.subTest("Checking status code"):
            self.assertEqual(response.status_code, 200)

        with self.subTest("User has a recipe"):
            self.assertEqual(response.context["user_recipes"][0].id, recipe.id)

    def test_recipe_preferred(self):
        response = self.client.get(reverse("koocook_core:recipe-all"))
        with self.subTest("Empty tag_set"):
            self.assertEqual(list(response.context["tag_set"]), [])

    def test_recipe_tags(self):
        response = self.client.get(reverse("koocook_core:recipe-tags"), {'name': ''})
        self.assertEqual(response.json()["current"], [])

    def test_recipe_search_listview(self):
        response = self.client.get(reverse("koocook_core:search"))

        with self.subTest("Search view must display all recipes with no filters"):
            self.assertEqual(list(response.context["object_list"].all()), [])

        recipe = create_dummy_recipe(self.author)
        response = self.client.get(reverse("koocook_core:search"), {'kw': recipe.name})
        with self.subTest("Search view must display recipes containing search keywords"):
            self.assertEqual(response.context["object_list"].all()[0].name, recipe.name)

        response = self.client.get(reverse("koocook_core:search"), {'popular': 'true'})
        self.client.get(reverse("koocook_core:recipe", kwargs={'recipe_id': recipe.id}))
        with self.subTest("Search by popularity alone"):
            self.assertEqual(response.context["object_list"][0].view_count, 1)

        response = self.client.get(reverse("koocook_core:search"), {'name_asc': '1'})
        self.client.get(reverse("koocook_core:recipe", kwargs={'recipe_id': recipe.id}))
        with self.subTest("Sort by name"):
            self.assertEqual(response.context["object_list"][0].id, recipe.id)


class RecipeVisitTest(AuthTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.recipe = create_dummy_recipe(self.author)
        self.visit = RecipeVisit.associate_recipe_with_user(self.kc_user, self.recipe)

    def test_unauthenticated_view(self):
        self.client.logout()
        response = self.client.get(reverse("koocook_core:recipe", kwargs={'recipe_id': self.recipe.id}))
        with self.subTest():
            self.assertEqual(response.context["object"].view_count, 2)
        response = self.client.get(reverse("koocook_core:recipe", kwargs={'recipe_id': self.recipe.id}))
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
        visit = RecipeVisit.associate_recipe_with_user(self.kc_user, self.recipe)
        with self.subTest():
            self.assertEqual(1, RecipeVisit.objects.all().count())

        with self.subTest("Getting the view count of a recipe"):
            self.assertEqual(self.recipe.recipevisit_set.all()[0], self.visit)
            self.assertEqual(1, self.recipe.view_count)

    def test_associate_recipe_visit_with_ip_address(self):
        self.request = RequestFactory()
        self.request = self.request.get('/')
        with self.subTest():
            self.assertEqual(get_client_ip(self.request), self.request.META.get('REMOTE_ADDR'))

        visit = RecipeVisit.associate_recipe_with_ip_address(self.request, self.recipe)
        with self.subTest():
            self.assertEqual(visit.ip_address, self.request.META.get('REMOTE_ADDR'))
            self.assertEqual(2, RecipeVisit.objects.all().count())
