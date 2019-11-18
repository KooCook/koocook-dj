from django import test as djangotest

from koocook_core import models


class TestAggregateRatingModel(djangotest.TestCase):
    def test_init_default_fields(self):
        pass

    def test_create_empty(self):
        pass

    def test_add_rating(self):
        pass

    def test_remove_rating(self):
        pass

    def test_check_rating(self):
        pass

    def test_item_reviewed_getter(self):
        pass

    def test_item_reviewed_setter(self):
        pass


class TestAuthorModel(djangotest.TestCase):
    def test_init(self):
        pass

    def test_str(self):
        pass

    def test_as_dict(self):
        pass

    def test_dj_user(self):
        pass

    def test_from_dj_user(self):
        pass

    def test_qualified_name(self):
        pass


class TestCommentModel(djangotest.TestCase):
    def test_init(self):
        pass

    def test_item_reviewed_getter(self):
        pass

    def test_item_reviewed_setter(self):
        pass


class TestMetaIngredientModel(djangotest.TestCase):
    def test_init(self):
        pass

    def test_field_nutrient(self):
        pass


class TestPostModel(djangotest.TestCase):
    def test_init(self):
        pass

    def test_as_dict(self):
        pass

    def test_processed_body(self):
        pass


class TestRecipeModel(djangotest.TestCase):
    def test_init(self):
        pass

    def test_total_time(self):
        pass


class TestTagLabelModel(djangotest.TestCase):
    def test_init(self):
        pass

    def test_field_normal_names_ok(self):
        pass

    def test_field_label_can_be_null(self):
        pass


class TestTagModel(djangotest.TestCase):
    def test_init(self):
        pass

    def test_field_normal_names_ok(self):
        pass


class TestRecipeIngredientModel(djangotest.TestCase):
    def test_init(self):
        pass

    def test_as_dict(self):
        pass

    def test_as_json(self):
        pass


class TestRatingModel(djangotest.TestCase):
    def test_init(self):
        pass

    def test_item_reviewed_getter(self):
        pass

    def test_item_reviewed_setter(self):
        pass


class TestKoocookUserModel(djangotest.TestCase):
    def test_init(self):
        pass

    def test_db_table_name(self):
        pass

    def test_follow(self):
        pass

    def test_unfollow(self):
        pass

    def test_name_getter(self):
        pass

    def test_full_name_getter(self):
        pass

    def test_as_dict(self):
        pass

    def test_as_json(self):
        pass


class TestQuantityField(djangotest.TestCase):
    def test_quantity_field_max_length(self):
        for model, field in (('RecipeIngredient', 'quantity'), ('Recipe', 'recipe_yield')):
            with self.subTest(model=model, field=field):
                m = getattr(models, model)()
                max_length = m._meta.get_field(field).max_length
                self.assertEqual(max_length, 40)
