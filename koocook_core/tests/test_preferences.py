from django.test import TestCase
from django.shortcuts import reverse
from django.contrib.auth.models import User

from ..support import PreferenceManager, TaggingPreference


class PreferencesTest(TestCase):
    def setUp(self) -> None:
        self.username = "testuser"
        password = "123$*HCfjdksla"
        self.user = User.objects.create_user(self.username, password=password)
        self.client.login(username=self.username, password=password)
        self.edit_pref_url = reverse('koocook_core:profile:pref-set')

    def test_default_preferences(self):
        manager = PreferenceManager()
        self.assertEqual(TaggingPreference.ALLOW_GLUTEN.full_name,
                         manager.get_full('allow_glut').full_name)

    def test_set_single_preference(self):
        import json
        response = self.client.post(self.edit_pref_url, {'preferences': json.dumps({'allow_glut': 'True'})})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, '{"status": "Preferences set", "current": {"allow_glut": "False"}}')
