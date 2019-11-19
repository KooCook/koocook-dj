from decimal import Decimal

from django import test as djangotest
from django.core.exceptions import ValidationError

from koocook_core import models
from koocook_core.tests import utils


class TestAggregateRatingModel(djangotest.TestCase):
    def test_field_settings(self):
        aggr = models.AggregateRating()
        with self.subTest(field='rating_value'):
            self.assertEqual(
                aggr._meta.get_field('rating_value').decimal_places,
                10)
            self.assertEqual(
                aggr._meta.get_field('rating_value').max_digits,
                13)

    def test_init_default_fields(self):
        aggr = models.AggregateRating()
        with self.subTest(field='best_rating'):
            self.assertEqual(aggr.best_rating, 5)
        with self.subTest(field='worst_rating'):
            self.assertEqual(aggr.worst_rating, 1)

    def test_create_empty(self):
        aggr = models.AggregateRating.create_empty()
        self.assertIsInstance(aggr, models.AggregateRating)
        self.assertEqual(aggr.best_rating, 5)
        self.assertEqual(aggr.worst_rating, 1)
        self.assertEqual(aggr.rating_value, 0)
        self.assertEqual(aggr.rating_count, 0)

    def test_item_reviewed_getter(self):
        with self.subTest(item=models.Post.__qualname__):
            item = models.Post()
            self.assertIs(item.aggregate_rating.post, item)
            self.assertIs(item.aggregate_rating.item_reviewed, item)

        with self.subTest(item=models.Recipe.__qualname__):
            item = models.Recipe()
            self.assertIs(item.aggregate_rating.recipe, item)
            self.assertIs(item.aggregate_rating.item_reviewed, item)

        with self.subTest(item=models.Comment.__qualname__):
            item = models.Comment()
            self.assertIs(item.aggregate_rating.comment, item)
            self.assertIs(item.aggregate_rating.item_reviewed, item)

    def test_check_rating(self):
        author = models.Author(name='author name')
        for cls in (models.Post, models.Recipe, models.Comment):
            with self.subTest(item=cls.__qualname__):
                item = cls()
                rating = models.Rating(author=author, rating_value=5)
                rating.item_reviewed = item
                try:
                    item.aggregate_rating.check_rating(rating)
                except Exception as e:
                    raise self.failureException('unexpected exception raised') from e

    def test_add_rating(self):
        author = models.Author(name='author name')
        for cls in (models.Post, models.Recipe, models.Comment):
            item = cls()
            # TODO: Add function to initialize Recipe and Post so that it is savable
            rating = models.Rating(author=author, rating_value=5)
            rating.item_reviewed = item
            with self.subTest(subtest='from empty', item=cls.__qualname__):
                item.aggregate_rating.add_rating(rating)
                self.assertEqual(item.aggregate_rating.rating_count, 1)
                self.assertEqual(item.aggregate_rating.rating_value, 5)
            rating = models.Rating(author=author, rating_value=3)
            rating.item_reviewed = item
            with self.subTest(subtest='add second', item=cls.__qualname__):
                item.aggregate_rating.add_rating(rating)
                self.assertEqual(item.aggregate_rating.rating_count, 2)
                self.assertEqual(item.aggregate_rating.rating_value, 4)
            # Re-using ratings should result in error
            with self.subTest(subtest='re-add rating', item=cls.__qualname__):
                with self.assertRaises(ValidationError):
                    item.aggregate_rating.add_rating(rating)

    def test_remove_rating(self):
        pass

    def test_add_rating_calculation_from_empty(self):
        # test special error prone values
        # add more as necessary
        for i in (0, 0., ):
            with self.subTest(i=i, old=(0, 0)):
                self.assertEqual(models.review._add_rating(Decimal(0), 0, i), i)
        # do monkey test, 999 is the maximum rating_value set
        for i in utils.gen_ints(-1000, 1000, 100):
            with self.subTest(i=i, old=(0, 0)):
                self.assertEqual(models.review._add_rating(Decimal(0), 0, i), i)
        for i in utils.gen_floats(-1000, 1000, 1_000):
            i = round(i, 1)
            with self.subTest(i=i, old=(0, 0)):
                # current use is with 1 decimal places for new ratings
                self.assertEqual(models.review._add_rating(Decimal(0), 0, i),
                                 round(Decimal(i), 1))

    def test_add_rating_calculation_from_nonempty(self):
        pass

    def test_remove_rating_calculation_from_empty(self):
        pass

    def test_remove_rating_calculation_from_nonempty(self):
        pass


class TestAuthorModel(djangotest.TestCase):
    def test_init(self):
        pass

    def test_str(self):
        pass

    def test_dj_user(self):
        pass

    def test_from_dj_user(self):
        pass

    def test_qualified_name(self):
        pass

    def test_as_dict(self):
        pass

    def test_as_json(self):
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

    def test_processed_body(self):
        pass

    def test_as_dict(self):
        pass

    def test_as_json(self):
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
