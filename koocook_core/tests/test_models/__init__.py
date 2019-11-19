import json
from decimal import Decimal

from django import test as djangotest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from koocook_core import models as models_
from koocook_core.models import *
from koocook_core.tests import utils


class TestAggregateRatingModel(djangotest.TestCase):
    def test_field_settings(self):
        aggr = AggregateRating()
        with self.subTest(field='rating_value'):
            self.assertEqual(
                aggr._meta.get_field('rating_value').decimal_places, 10)
        with self.subTest(field='rating_value'):
            self.assertEqual(
                aggr._meta.get_field('rating_value').max_digits, 13)

    def test_init_default_fields(self):
        aggr = AggregateRating()
        with self.subTest(field='best_rating'):
            self.assertEqual(aggr.best_rating, 5)
        with self.subTest(field='worst_rating'):
            self.assertEqual(aggr.worst_rating, 1)

    def test_create_empty(self):
        aggr = AggregateRating.create_empty()
        with self.subTest('type'):
            self.assertIsInstance(aggr, AggregateRating)
        for attr, value in (
            ('best_rating', 5),
            ('worst_rating', 1),
            ('rating_value', 0),
            ('rating_count', 0),
        ):
            with self.subTest('values', attr=attr):
                self.assertEqual(getattr(aggr, attr), value)

    def test_item_reviewed_getter(self):
        for cls in (Post, Recipe, Comment):
            with self.subTest(item=cls.__qualname__):
                item = cls()
                self.assertIs(
                    getattr(item.aggregate_rating, cls.__name__.lower()), item)
                self.assertIs(item.aggregate_rating.item_reviewed, item)

    def test_check_rating(self):
        author = Author(name='author name')
        for cls in (Post, Recipe, Comment):
            with self.subTest(item=cls.__qualname__):
                item = cls()
                rating = Rating(author=author, rating_value=5)
                rating.item_reviewed = item
                try:
                    item.aggregate_rating.check_rating(rating)
                except Exception as e:
                    raise self.failureException(
                        'unexpected exception raised') from e

    def test_add_rating(self):
        author = Author(name='author name')
        for cls in (Post, Recipe, Comment):
            item = cls()
            # TODO: Add function to initialize Recipe and Post so that it is savable
            rating = Rating(author=author, rating_value=5)
            rating.item_reviewed = item
            with self.subTest('from empty', item=cls.__qualname__):
                item.aggregate_rating.add_rating(rating)
                self.assertEqual(item.aggregate_rating.rating_count, 1)
                self.assertEqual(item.aggregate_rating.rating_value, 5)

            rating = Rating(author=author, rating_value=3)
            rating.item_reviewed = item
            with self.subTest('add second', item=cls.__qualname__):
                item.aggregate_rating.add_rating(rating)
                self.assertEqual(item.aggregate_rating.rating_count, 2)
                self.assertEqual(item.aggregate_rating.rating_value, 4)

            # Re-using ratings should result in error
            with self.subTest('re-add rating', item=cls.__qualname__):
                with self.assertRaises(ValidationError):
                    item.aggregate_rating.add_rating(rating)

    def test_remove_rating(self):
        pass

    def test_add_rating_calculation_from_empty(self):
        # test special error prone values
        # add more as necessary
        for i in (0, 0.):
            with self.subTest('test manual', i=i, old=(0, 0)):
                self.assertEqual(review._add_rating(Decimal(0), 0, i), i)

        # do monkey test, 999 is the maximum rating_value set
        for i in utils.gen_ints(-1000, 1000, 100):
            with self.subTest('test int', i=i, old=(0, 0)):
                self.assertEqual(review._add_rating(Decimal(0), 0, i), i)

        for i in utils.gen_floats(-1000, 1000, 1_000):
            i = round(i, 1)
            with self.subTest('test float', i=i, old=(0, 0)):
                # current use is with 1 decimal places for new ratings
                self.assertEqual(review._add_rating(Decimal(0), 0, i),
                                 round(Decimal(i), 1))

    # TODO: Add these tests

    def test_add_rating_calculation_from_nonempty(self):
        pass

    def test_remove_rating_calculation_from_empty(self):
        pass

    def test_remove_rating_calculation_from_nonempty(self):
        pass


class TestAuthorModel(djangotest.TestCase):
    def setUp(self) -> None:
        self.test_user = User.objects.create(username='AliceWonder',
                                             first_name='Alice',
                                             last_name='Merryweather')
        self.test_author = Author.objects.create(name='Bobby Brown')

    def test_field_settings(self):
        with self.subTest(field='name'):
            self.assertEqual(
                self.test_author._meta.get_field('name').max_length, 100)
        with self.subTest(field='koocook_user'):
            self.assertTrue(
                self.test_author._meta.get_field('koocook_user').null)

    def test_str(self):
        for expected_str, user in (
            ('Alice Merryweather', self.test_user),
            ('Bob', User.objects.create(first_name='Bob', username='Bobby')),
            ('C123', User.objects.create(username='C123')),
            ('Dylan', User.objects.create(last_name='Dylan', username='DD')),
        ):
            with self.subTest('author with user',
                              first_name=user.first_name,
                              last_name=user.last_name,
                              username=user.username):
                self.assertEqual(expected_str, str(user.koocookuser.author))
        for name in ('Ethan Ethanoate', 'Farseer'):
            with self.subTest('author without user', name=name):
                author = Author.objects.create(name=name)
                self.assertEqual(str(author), author.name)
        # Note for review:
        #   This test is only made based on the actual implementation

    def test_dj_user(self):
        self.assertIs(self.test_user.koocookuser.author.dj_user,
                      self.test_user)

    def test_from_dj_user(self):
        self.assertIs(Author.from_dj_user(self.test_user),
                      self.test_user.koocookuser.author)
        # Note for review:
        #   This function seems unnecessary
        #   (one dot away but doesn't need importing Author)

    def test_qualified_name(self):
        pass
        # Note for review:
        #   This test is only made based on the actual implementation

    def test_as_dict(self):
        pass
        # Note for review:
        #   This test is only made based on the actual implementation

    def test_as_json(self):
        # TODO: Fix this test
        with self.subTest('author with user'):
            self.assertEqual(
                json.loads(self.test_user.koocookuser.author.as_json),
                self.test_user.koocookuser.author.as_dict)
        with self.subTest('author without user'):
            self.assertEqual(json.loads(self.test_author.as_json),
                             self.test_author.as_dict)


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
        for model, field in (
            ('RecipeIngredient', 'quantity'),
            ('Recipe', 'recipe_yield'),
        ):
            with self.subTest(model=model, field=field):
                m = getattr(models_, model)()
                max_length = m._meta.get_field(field).max_length
                self.assertEqual(max_length, 50)
