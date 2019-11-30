from datetime import timedelta
from django.shortcuts import reverse
from koocook_core.models.recipe import Recipe, RecipeVisit, get_client_ip
from .base import create_dummy_recipe, AuthTestCase
from django.test import TestCase, RequestFactory
from koocook_core.tests.base import AuthTestCase, create_dummy_recipe


class RecipeTests(AuthTestCase):
    def test_total_time_with_prep_cook_time_are_second(self):
        time = timedelta(seconds=30)
        recipe = Recipe(prep_time=time, cook_time=time)
        self.assertEqual(recipe.total_time, timedelta(minutes=1))

    def test_total_time_with_prep_time_cook_time(self):
        time = timedelta(seconds=30)
        recipe = Recipe(prep_time=time, cook_time=time)
        self.assertEqual(recipe.total_time, timedelta(minutes=1))

    def test_total_time_with_zero_prep_time(self):
        recipe = Recipe(prep_time=timedelta(seconds=90), cook_time=timedelta(seconds=0))
        self.assertEqual(recipe.total_time, timedelta(minutes=1, seconds=30))

    def test_recipe_ingredient(self):
        recipe = Recipe()
        self.assertEqual(list(recipe.recipe_ingredients.all()), list(recipe.recipeingredient_set.all()))
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

    def test_recipe_update_view_context(self):
        recipe = create_dummy_recipe(self.author)
        response = self.client.get(reverse("koocook_core:recipe-edit", kwargs={'pk': recipe.id}))
        with self.subTest():
            self.assertEqual(response.context["ingredients"], '[]')
        with self.subTest():
            self.assertEqual(response.context["tags"], '[]')

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

    def test_recipe_search_listview(self):
        response = self.client.get(reverse("koocook_core:search"))

        with self.subTest("Search view must display all recipes with no filters"):
            self.assertEqual(list(response.context["object_list"].all()), [])

        recipe = create_dummy_recipe(self.author)
        response = self.client.get(reverse("koocook_core:search"), {'kw': recipe.name})
        with self.subTest("Search view must display recipes containing search keywords"):
            self.assertEqual(response.context["object_list"].all()[0].name, recipe.name)


class RecipeVisitTest(AuthTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.recipe = create_dummy_recipe(self.author)
        self.visit = RecipeVisit.associate_recipe_with_user(self.kc_user, self.recipe)

    def test_visit_count(self):
        with self.subTest():
            self.assertEqual(1, RecipeVisit.objects.all().count())
        self.recipe.delete()
        with self.subTest():
            self.assertEqual(0, RecipeVisit.objects.all().count())

    def test_visit_count_of_user(self):
        self.kc_user.delete()
        with self.subTest():
            self.assertEqual(1, RecipeVisit.objects.all().count())
        with self.subTest():
            self.assertEqual(self.visit.user.id, None)

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
        visit.save()
        with self.subTest():
            self.assertEqual(visit.ip_address, self.request.META.get('REMOTE_ADDR'))
            self.assertEqual(2, RecipeVisit.objects.all().count())
