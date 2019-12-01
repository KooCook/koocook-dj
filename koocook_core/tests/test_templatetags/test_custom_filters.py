from django.test import TestCase
from koocook_core.models.tag import TagLabel
from koocook_core.templatetags.recipe_extras import tag_level


class CustomTagTests(TestCase):
    def test_tag_level(self):
        tag_label = create_tag_label(name='label 1', level=4)
        self.assertEqual(tag_level(tag_label.level), 'is-danger')

    def test_tag_level_with_over_level(self):
        tag_label = create_tag_label(name='label 1', level=100)
        self.assertIsNone(tag_level(tag_label.level))


def create_tag_label(name: str, level: int = 1):
    return TagLabel.objects.create(name=name, level=level)
