from datetime import timedelta
from django.test import TestCase, RequestFactory
from koocook_core.tests.base import AuthTestCase, create_dummy_recipe
from koocook_core.models.recipe import Recipe, RecipeVisit, get_client_ip


class RecipeModelTests(TestCase):
    def test_total_time_with_prep_cook_time_are_second(self):
        time = timedelta(seconds=30)
        recipe = Recipe(prep_time=time, cook_time=time)
        self.assertEqual(recipe.total_time, timedelta(minutes=1))


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
