import datetime
from django.test import TestCase
from koocook_core.models.tag import TagLabel
from koocook_core.templatetags.recipe_extras import tag_level, duration_in_words


class CustomTagTests(TestCase):
    def test_tag_level(self):
        tag_label = create_tag_label(name='label 1', level=4)
        self.assertEqual(tag_level(tag_label.level), 'is-danger')

    def test_tag_level_with_over_level(self):
        tag_label = create_tag_label(name='label 1', level=100)
        self.assertIsNone(tag_level(tag_label.level))


class DurationWordsTests(TestCase):
    def test_mixed(self):
        duration = datetime.timedelta(days=2, hours=1, minutes=1)
        with self.subTest():
            self.assertEqual(duration_in_words(None), "N/A")
        with self.subTest():
            self.assertEqual(duration_in_words(duration), "2 days 1 hour 1 minute")
        duration = datetime.timedelta(hours=3, minutes=1, seconds=2)
        with self.subTest():
            self.assertEqual(duration_in_words(duration), "3 hours 1 minute 2 seconds")
        duration = datetime.timedelta(minutes=1)
        with self.subTest():
            self.assertEqual(duration_in_words(duration), "1 minute")
        duration = datetime.timedelta(minutes=3)
        with self.subTest():
            self.assertEqual(duration_in_words(duration), "3 minutes")
        duration = datetime.timedelta(seconds=12)
        with self.subTest():
            self.assertEqual(duration_in_words(duration), "12 seconds")


def create_tag_label(name: str, level: int = 1):
    return TagLabel.objects.create(name=name, level=level)
