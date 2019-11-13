from django import test as djangotest

from koocook_core import models


class TestAggregateRatingModel(djangotest.TestCase):
    pass


class TestAuthorModel(djangotest.TestCase):
    pass


class TestCommentModel(djangotest.TestCase):
    pass


class TestMetaIngredientModel(djangotest.TestCase):
    pass


class TestPostModel(djangotest.TestCase):
    pass


class TestRecipeModel(djangotest.TestCase):
    pass


class TestTagLabelModel(djangotest.TestCase):
    pass


class TestTagModel(djangotest.TestCase):
    pass


class TestRecipeIngredientModel(djangotest.TestCase):
    pass


class TestQuantityField(djangotest.TestCase):
    def test_quantity_field_max_length(self):
        for model, field in (('RecipeIngredient', 'quantity'), ('Recipe', 'recipe_yield')):
            with self.subTest(model=model, field=field):
                m = getattr(models, model)()
                max_length = m._meta.get_field(field).max_length
                self.assertEqual(max_length, 40)
