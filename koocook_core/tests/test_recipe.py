from datetime import timedelta
from django.shortcuts import reverse
from koocook_core.models.recipe import Recipe
from .base import create_dummy_recipe, AuthTestCase


class RecipeModelTests(AuthTestCase):
    def test_total_time_with_prep_cook_time_are_second(self):
        time = timedelta(seconds=30)
        recipe = Recipe(prep_time=time, cook_time=time)
        self.assertEqual(recipe.total_time, timedelta(minutes=1))

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
        recipe = create_dummy_recipe(self.user)
        response = self.client.get(reverse("koocook_core:recipe", kwargs={'recipe_id': recipe.id}))
        self.assertEqual(response.context["ingredients"], [])

    def test_recipe_update_view_context(self):
        recipe = create_dummy_recipe(self.user)
        response = self.client.get(reverse("koocook_core:recipe-edit", kwargs={'pk': recipe.id}))
        with self.subTest():
            self.assertEqual(response.context["ingredients"], '[]')
        with self.subTest():
            self.assertEqual(response.context["tags"], '[]')

    def test_recipe_user_listview(self):
        response = self.client.get(reverse("koocook_core:recipe-user"))
        with self.subTest("User has no recipes"):
            self.assertEqual(list(response.context["user_recipes"]), [])
        recipe = create_dummy_recipe(self.user)
        response = self.client.get(reverse("koocook_core:recipe-user"))
        with self.subTest("User has a recipe"):
            self.assertEqual(response.context["user_recipes"].all()[0].id, recipe.id)

    def test_recipe_search_listview(self):
        response = self.client.get(reverse("koocook_core:search"))
        recipe = create_dummy_recipe(self.user)
        with self.subTest("Search view must display all recipes with no filters"):
            self.assertEqual(list(response.context["recipes"].all()), [])

        response = self.client.get(reverse("koocook_core:search"), {'kw': recipe.name})
        with self.subTest("Search view must display recipes containing search keywords"):
            self.assertEqual(response.context["recipes"].all()[0].name, recipe.name)
