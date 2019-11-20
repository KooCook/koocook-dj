import json
from decimal import Decimal
from typing import List, Union
import itertools

from django import test as djangotest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
import names

from koocook_core import models as models_
from koocook_core.models import *
from koocook_core.support import Quantity
from koocook_core.support.fraction import Fraction
from koocook_core.tests import utils


def set_up_authors(n: int = 5) -> List[Author]:
    test_authors = []
    for _ in range(n):
        test_authors.append(Author.objects.create(name=names.get_full_name()))
        test_authors.append(
            User.objects.create(
                first_name=names.get_first_name(),
                last_name=names.get_last_name()).koocookuser.author)
    return test_authors


def set_up_reviewables(authors: List[Author]
                       ) -> List[Union[Recipe, Post, Comment]]:
    test_objects = []
    for author in authors:
        recipe = Recipe.objects.create(author=author, name='recipe name')
        post = Post.objects.create(author=author)
        test_objects.extend([recipe, post])
    for author in authors:
        for obj in test_objects.copy():
            comment = Comment.objects.create(author=author, item_reviewed=obj)
            test_objects.append(comment)
    return test_objects


class TestAggregateRatingModel(djangotest.TestCase):
    def setUp(self) -> None:
        self.test_authors = set_up_authors()
        self.test_objects = set_up_reviewables(self.test_authors)

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
                with self.subTest(author=author,
                                  item=item.__class__.__qualname__):
                    rating = Rating(author=author,
                                    rating_value=5,
                                    item_reviewed=item)
                    try:
                        item.aggregate_rating.check_rating(rating)
                    except Exception as e:
                        raise self.failureException(
                            'unexpected exception raised') from e

    def test_add_rating(self):
        for author in self.test_authors:
            for item in self.test_objects:
                rating = Rating(author=author,
                                rating_value=5,
                                item_reviewed=item)
                with self.subTest('from empty',
                                  author=author,
                                  item=item.__class__.__qualname__):
                    item.aggregate_rating.add_rating(rating)
                    self.assertEqual(item.aggregate_rating.rating_count, 1)
                    self.assertEqual(item.aggregate_rating.rating_value, 5)

                rating = Rating(author=author,
                                rating_value=3,
                                item_reviewed=item)
                with self.subTest('add second',
                                  author=author,
                                  item=item.__class__.__qualname__):
                    item.aggregate_rating.add_rating(rating)
                    self.assertEqual(item.aggregate_rating.rating_count, 2)
                    self.assertEqual(item.aggregate_rating.rating_value, 4)

                # Re-using ratings should result in error
                with self.subTest('re-add rating',
                                  author=author,
                                  item=item.__class__.__qualname__):
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
                self.assertEqual(models_.review._add_rating(Decimal(0), 0, i),
                                 i)

        # do monkey test, 999 is the maximum rating_value set
        for i in utils.gen_ints(-1000, 1000, 100):
            with self.subTest('test int', i=i, old=(0, 0)):
                self.assertEqual(models_.review._add_rating(Decimal(0), 0, i),
                                 i)

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
        self.assertEqual(Author.from_dj_user(self.test_user),
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
        pass
        # TODO: Fix this test
        # with self.subTest('author with user'):
        #     self.assertEqual(
        #         json.loads(self.test_user.koocookuser.author.as_json),
        #         self.test_user.koocookuser.author.as_dict)
        # with self.subTest('author without user'):
        #     self.assertEqual(json.loads(self.test_author.as_json),
        #                      self.test_author.as_dict)


class TestCommentModel(djangotest.TestCase):
    def setUp(self) -> None:
        self.test_user = User.objects.create(username='AliceWonder',
                                             first_name='Alice',
                                             last_name='Merryweather')
        self.test_author = Author.objects.create(name='Bobby Brown')

    def test_init(self):
        recipe = Recipe.objects.create(author=self.test_author, name='')
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
        recipe = Recipe.objects.create(author=self.test_author, name='')
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
                self.assertLess(now - post.date_published,
                                timezone.timedelta(seconds=1))
                self.assertGreaterEqual(now - post.date_published,
                                        timezone.timedelta(0))

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
        for field, attr, value in (('name', 'max_length', 255), ):
            with self.subTest(field=field, attr=attr):
                self.assertEqual(getattr(recipe._meta.get_field(field), attr),
                                 value)
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
            with self.subTest(field='aggregate_rating',
                              author=author,
                              name=name):
                aggr = recipe.aggregate_rating
                self.assertEqual(aggr.rating_count, 0)
                self.assertEqual(aggr.rating_value, 0)
                self.assertIs(aggr.recipe, recipe)
            with self.subTest(field='date_published', autor=author, name=name):
                now = timezone.now()
                self.assertLess(now - recipe.date_published,
                                timezone.timedelta(seconds=1))
                self.assertGreaterEqual(now - recipe.date_published,
                                        timezone.timedelta(0))
            with self.subTest(field='recipe_instructions',
                              autor=author,
                              name=name):
                # use Equal instead of ListEqual for possible changes in data structure
                self.assertEqual(recipe.recipe_instructions, [])

    # TODO: Add test to validate fields (prep_time and cook_time must be postive, e.g.)

    def test_init(self):
        # TODO: Test common actual recipes
        for author in self.test_authors:
            with self.subTest():
                Recipe.objects.create(name='Buttermilk Pancakes',
                                      author=author)

    def test_total_time(self):
        td = timezone.timedelta
        # monkey test should be enough for library code, you just have to be sure
        # the operation is add and not something else
        for unit in ('seconds', 'minutes', 'hours'):
            for a, b in zip(utils.gen_ints(0, 1000, 100),
                            utils.gen_ints(0, 1000, 100)):
                with self.subTest(a=a, b=b, unit=unit):
                    recipe = Recipe(prep_time=td(**{unit: a}),
                                    cook_time=td(**{unit: b}))
                    self.assertEqual(recipe.total_time, td(**{unit: a + b}))
        for a, b, c in zip(utils.gen_ints(0, 1000, 100),
                           utils.gen_ints(0, 1000, 100),
                           utils.gen_ints(0, 1000, 100)):
            with self.subTest(a=a, b=b, unit=unit):
                recipe = Recipe(prep_time=td(hours=a, minutes=b, seconds=c),
                                cook_time=td(hours=b, minutes=c, seconds=a))
                self.assertEqual(recipe.total_time,
                                 td(hours=a + b, minutes=b + c, seconds=c + a))


class TestTagLabelModel(djangotest.TestCase):
    def test_init(self):
        # TODO: add more cases
        with self.subTest('common values'):
            label = TagLabel.objects.create(name='cuisine')
            tag = Tag.objects.create(name='French', label=label)
        with self.subTest('duplicates'):
            with self.assertRaises(ValueError):
                tag = Tag.objects.create(name='French', label=label)
            try:
                tag = Tag.objects.create(name='Chinese', label=label)
            except Exception as e:
                raise self.failureException(
                    'unexpected exception raised') from e

    def test_fields_settings(self):
        tag = Tag()
        with self.subTest(field='name', attr='max_length'):
            self.assertEqual(tag._meta.get_field('name').max_length, 50)
        with self.subTest(field='label', attr='null'):
            self.assertTrue(tag._meta.get_field('label').null)
        with self.subTest(field='label', attr='blank'):
            self.assertTrue(tag._meta.get_field('label').blank)


class TestTagModel(djangotest.TestCase):
    def test_init(self):
        # TODO: add more cases
        with self.subTest('common values'):
            label = TagLabel.objects.create(name='cuisine')
        with self.subTest('duplicates'):
            with self.assertRaises(ValueError):
                label = TagLabel.objects.create(name='cuisine')

    def test_fields_settings(self):
        label = TagLabel()
        with self.subTest(field='name', attr='max_length'):
            self.assertEqual(label._meta.get_field('name').max_length, 50)


class TestRecipeIngredientModel(djangotest.TestCase):
    def test_init(self):
        # TODO: test common values
        quantity = Quantity(Fraction(1, 2), 'tbsp')
        mi = MetaIngredient.objects.create(name='')
        recipe = Recipe.objects.create(name='')
        ri = RecipeIngredient.objects.create(quantity=quantity,
                                             meta=mi,
                                             recipe=recipe)

    def test_fields_settings(self):
        ri = RecipeIngredient()
        with self.subTest(field='substitute_set', attr='blank'):
            self.assertTrue(ri._meta.get_field('substitute_set').blank)
        for field, attr in (
            ('quantity', 'null'),
            ('quantity', 'blank'),
            ('meta', 'null'),
            ('meta', 'blank'),
            ('recipe', 'null'),
            ('recipe', 'blank'),
        ):
            with self.subTest(field=field, attr=attr):
                self.assertFalse(getattr(ri._meta.get_field(field), attr))

    def test_as_dict(self):
        pass

    def test_as_json(self):
        pass

    def test_nutrition(self):
        pass


class TestRatingModel(djangotest.TestCase):
    def setUp(self) -> None:
        self.test_authors = set_up_authors()
        self.test_objects = set_up_reviewables(self.test_authors)

    def test_init(self):
        for author in self.test_authors:
            for item in self.test_objects:
                with self.subTest('typical', author=author, item=item):
                    rating = Rating(author=author,
                                    rating_value=3,
                                    item_reviewed=item)
                with self.subTest('boundary', author=author, item=item):
                    rating = Rating(author=author,
                                    rating_value=5,
                                    item_reviewed=item)
                    rating = Rating(author=author,
                                    rating_value=1,
                                    item_reviewed=item)
                with self.subTest('failing', author=author, item=item):
                    with self.assertRaises(ValueError):
                        rating = Rating(author=author,
                                        rating_value=6,
                                        item_reviewed=item)
                    with self.assertRaises(ValueError):
                        rating = Rating(author=author,
                                        rating_value=0,
                                        item_reviewed=item)

    def test_item_reviewed_getter(self):
        # TODO: Fix duplicate code
        for item in self.test_objects:
            with self.subTest(item=item.__class__.__qualname__):
                self.assertIs(
                    getattr(item.aggregate_rating,
                            item.__class__.__name__.lower()), item)
                self.assertIs(item.aggregate_rating.item_reviewed, item)


class TestKoocookUserModel(djangotest.TestCase):
    def setUp(self) -> None:
        self.test_kc_users = [
            User.objects.create(first_name=names.get_first_name(),
                                last_name=names.get_last_name(),
                                username=names.get_full_name()).koocookuser
            for _ in range(10)
        ]

    def clean_up_followings(self):
        for kc in self.test_kc_users:
            kc.followers.clear()
            kc.following.clear()
            kc.save()

    def test_fields_default(self):
        kc = KoocookUser()
        self.assertEqual(kc.preferences, {})
        self.assertEqual(kc.user_settings, {})

    def test_db_table_name(self):
        kc = KoocookUser()
        self.assertEqual(kc._meta.db_table, 'koocook_core_koocook_user')

    def test_follow(self):
        for follower, followee in zip(*itertools.tee(self.test_kc_users, 2)):
            follower.follow(followee)
            with self.subTest(follower=follower, followee=followee):
                self.assertIn(follower, followee.followers.all())
            with self.subTest(follower=follower, followee=followee):
                self.assertIn(followee, follower.following.all())
        self.clean_up_followings()

    def test_unfollow(self):
        for follower, followee in zip(*itertools.tee(self.test_kc_users, 2)):
            follower.follow(followee)
            follower.unfollow(followee)
            with self.subTest(follower=follower, followee=followee):
                self.assertNotIn(follower, followee.followers.all())
            with self.subTest(follower=follower, followee=followee):
                self.assertNotIn(followee, follower.following.all())
        self.clean_up_followings()

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
