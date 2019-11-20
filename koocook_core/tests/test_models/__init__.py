import json
from decimal import Decimal

from django import test as djangotest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from koocook_core import models as models_
from koocook_core.models import *
from koocook_core.tests import utils


class TestAggregateRatingModel(djangotest.TestCase):

    def setUp(self) -> None:
        author = Author.objects.create(name='')
        user = User.objects.create(email='koocook@gmail.com')
        self.test_authors = [author, user.koocookuser.author]
        self.test_objects = []

        for author in self.test_authors:
            recipe = Recipe.objects.create(author=author,
                                           name='recipe name',
                                           recipe_instructions=[])
            post = Post.objects.create(author=author)
            self.test_objects.extend([recipe, post])

        for author in self.test_authors:
            for obj in self.test_objects.copy():
                comment = Comment.objects.create(author=author, item_reviewed=obj)
                self.test_objects.append(comment)

    def clean_up_aggregate_rating(self):
        """Resets the state of aggregate ratings, for testing only."""
        for item in self.test_objects:
            aggr = item.aggregate_rating
            aggr.rating_value = 0
            aggr.rating_count = 0
            aggr.save()

    def test_fields_settings(self):
        aggr = AggregateRating()
        with self.subTest(field='rating_value'):
            self.assertEqual(
                aggr._meta.get_field('rating_value').decimal_places, 10)
        with self.subTest(field='rating_value'):
            self.assertEqual(
                aggr._meta.get_field('rating_value').max_digits, 13)

    def test_fields_default(self):
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
        for item in self.test_objects:
            with self.subTest(item=item.__class__.__qualname__):
                self.assertIs(
                    getattr(item.aggregate_rating,
                            item.__class__.__name__.lower()), item)
                self.assertIs(item.aggregate_rating.item_reviewed, item)

    def test_check_rating(self):
        for author in self.test_authors:
            for item in self.test_objects:
                with self.subTest(author=author, item=item.__class__.__qualname__):
                    rating = Rating(author=author, rating_value=5)
                    rating.item_reviewed = item
                    try:
                        item.aggregate_rating.check_rating(rating)
                    except Exception as e:
                        raise self.failureException(
                            'unexpected exception raised') from e

    def test_add_rating(self):
        for author in self.test_authors:
            for item in self.test_objects:
                rating = Rating(author=author, rating_value=5)
                rating.item_reviewed = item
                with self.subTest('from empty', author=author, item=item.__class__.__qualname__):
                    item.aggregate_rating.add_rating(rating)
                    self.assertEqual(item.aggregate_rating.rating_count, 1)
                    self.assertEqual(item.aggregate_rating.rating_value, 5)

                rating = Rating(author=author, rating_value=3)
                rating.item_reviewed = item
                with self.subTest('add second', author=author, item=item.__class__.__qualname__):
                    item.aggregate_rating.add_rating(rating)
                    self.assertEqual(item.aggregate_rating.rating_count, 2)
                    self.assertEqual(item.aggregate_rating.rating_value, 4)

                # Re-using ratings should result in error
                with self.subTest('re-add rating', author=author, item=item.__class__.__qualname__):
                    with self.assertRaises(ValidationError):
                        item.aggregate_rating.add_rating(rating)
            self.clean_up_aggregate_rating()

    def test_remove_rating(self):
        pass

    def test_add_rating_calculation_from_empty(self):
        # test special error prone values
        # add more as necessary
        for i in (0, 0.):
            with self.subTest('test manual', i=i, old=(0, 0)):
                self.assertEqual(models_.review._add_rating(Decimal(0), 0, i), i)

        # do monkey test, 999 is the maximum rating_value set
        for i in utils.gen_ints(-1000, 1000, 100):
            with self.subTest('test int', i=i, old=(0, 0)):
                self.assertEqual(models_.review._add_rating(Decimal(0), 0, i), i)

        for i in utils.gen_floats(-1000, 1000, 1_000):
            i = round(i, 1)
            with self.subTest('test float', i=i, old=(0, 0)):
                # current use is with 1 decimal places for new ratings
                self.assertEqual(models_.review._add_rating(Decimal(0), 0, i),
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
    def setUp(self) -> None:
        self.test_user = User.objects.create(username='AliceWonder',
                                             first_name='Alice',
                                             last_name='Merryweather')
        self.test_author = Author.objects.create(name='Bobby Brown')

    def test_init(self):
        recipe = Recipe.objects.create(author=self.test_author,
                                       name='',
                                       recipe_instructions=[])
        post = Post.objects.create(author=self.test_author)
        for name in ('Recipe', 'Post', 'Comment'):
            item = locals()[name.lower()]
            with self.subTest(item_reviewed=name):
                try:
                    comment = Comment.objects.create(author=self.test_author,
                                                     item_reviewed=item)
                except Exception as e:
                    raise self.failureException(
                        'unexpected exception raised') from e

    def test_item_reviewed_getter(self):
        recipe = Recipe.objects.create(author=self.test_author,
                                       name='',
                                       recipe_instructions=[])
        post = Post.objects.create(author=self.test_author)
        for name in ('Recipe', 'Post', 'Comment'):
            item = locals()[name.lower()]
            with self.subTest(item_reviewed=name):
                comment = Comment.objects.create(author=self.test_author,
                                                 item_reviewed=item)
                self.assertIs(comment.item_reviewed, item)


class TestMetaIngredientModel(djangotest.TestCase):
    def test_fields_setting(self):
        mi = MetaIngredient()
        with self.subTest(field='name'):
            self.assertEqual(mi._meta.get_field('name').max_length, 255)
        with self.subTest(field='description'):
            self.assertEqual(mi._meta.get_field('description').max_length, 255)

    def test_fields_default(self):
        mi = MetaIngredient()
        with self.subTest(field='nutrient'):
            self.assertEqual(mi.nutrient, {})


class TestPostModel(djangotest.TestCase):
    def setUp(self) -> None:
        author = Author.objects.create(name='Bobby Brown')
        user = User.objects.create(email='alicewonder@gmail.com')
        self.test_authors = [author, user.koocookuser.author]

    def test_fields_default(self):
        for author in self.test_authors:
            post = Post.objects.create(author=author)
            with self.subTest('aggregate rating', author=author):
                aggr = post.aggregate_rating
                self.assertEqual(aggr.rating_count, 0)
                self.assertEqual(aggr.rating_value, 0)
                self.assertIs(aggr.post, post)
            with self.subTest('date published', autor=author):
                now = timezone.now()
                self.assertLess(now - post.date_published, timezone.timedelta(seconds=1))
                self.assertGreaterEqual(now - post.date_published, timezone.timedelta(0))

    def test_init(self):
        # TODO: Test common actual posts
        for author in self.test_authors:
            with self.subTest('creation', author=author):
                try:
                    post = Post.objects.create(author=author)
                except Exception as e:
                    raise self.failureException(
                        'unexpected exception raised') from e

    def test_as_dict(self):
        pass

    def test_as_json(self):
        pass


class TestRecipeModel(djangotest.TestCase):
    def setUp(self) -> None:
        author = Author.objects.create(name='Bobby Brown')
        user = User.objects.create(email='alicewonder@gmail.com')
        self.test_authors = [author, user.koocookuser.author]

    def test_fields_setting(self):
        recipe = Recipe()
        for field, attr, value in (
                ('name', 'max_length', 255),
        ):
            with self.subTest(field=field, attr=attr):
                self.assertEqual(getattr(recipe._meta.get_field(field), attr), value)
        for field, attr in (
                ('image', 'null'),
                ('image', 'blank'),
                ('video', 'null'),
                ('video', 'blank'),
                ('author', 'null'),
                ('date_published', 'null'),
                ('prep_time', 'null'),
                ('cook_time', 'null'),
                ('recipe_yield', 'null'),
                ('tag_set', 'blank'),
                ('aggregate_rating', 'blank'),
        ):
            with self.subTest(field=field, attr=attr):
                self.assertTrue(getattr(recipe._meta.get_field(field), attr))
        for field, attr in (
                ('name', 'null'),
                ('name', 'blank'),
                ('author', 'blank'),
                ('date_published', 'blank'),
                ('prep_time', 'blank'),
                ('cook_time', 'blank'),
                ('recipe_instructions', 'null'),
                ('recipe_instructions', 'blank'),
                ('recipe_yield', 'blank'),
        ):
            with self.subTest(field=field, attr=attr):
                self.assertFalse(getattr(recipe._meta.get_field(field), attr))

    def test_fields_default(self):
        for author in self.test_authors:
            name = 'Buttermilk Pancakes'
            recipe = Recipe.objects.create(author=author, name=name)
            with self.subTest(field='aggregate_rating', author=author, name=name):
                aggr = recipe.aggregate_rating
                self.assertEqual(aggr.rating_count, 0)
                self.assertEqual(aggr.rating_value, 0)
                self.assertIs(aggr.recipe, recipe)
            with self.subTest(field='date_published', autor=author, name=name):
                now = timezone.now()
                self.assertLess(now - recipe.date_published, timezone.timedelta(seconds=1))
                self.assertGreaterEqual(now - recipe.date_published, timezone.timedelta(0))
            with self.subTest(field='recipe_instructions', autor=author, name=name):
                # use Equal instead of ListEqual for possible changes in data structure
                self.assertEqual(recipe.recipe_instructions, [])

    def test_init(self):
        # TODO: Test common actual recipes
        for author in self.test_authors:
            with self.subTest():
                Recipe.objects.create(name='Buttermilk Pancakes', author=author)

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
