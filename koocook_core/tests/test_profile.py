import json
from django.test import TestCase
from django.shortcuts import reverse
from django.contrib.auth.models import User

from .base import AuthTestCase
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
        self.assertEqual(TaggingPreference.PREFERRED_TAGS.full_name,
                         manager.get_full('preferred_tags').full_name)

    def test_set_single_preference(self):
        response = self.client.post(self.edit_pref_url, {'preferences': json.dumps({'preferred_tags': []})})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, '{"status": "Preferences set", "current": {"preferred_tags": []}}')


class UserProfileTest(AuthTestCase):
    def test_user_profile_view(self):
        response = self.client.get(reverse("koocook_core:profile:info"))
        self.assertTemplateUsed(response, 'users/info.html')

    def test_user_preferred_recipes(self):
        self.kc_user.formal_preferences['preferred_tags'] = [{"name":"Meat","label":{"name":"","level":1}}]
        self.kc_user.preferences = self.kc_user.formal_preferences.serialised_preferences
        response = self.client.get(reverse("koocook_core:recipe-all"))
        with self.subTest():
            self.assertEqual(response.status_code, 200)

    def test_user_settings_post(self):
        response = self.client.post(reverse("koocook_core:profile:pref"), {
            'preferences': '{}'
        })
        with self.subTest("Checking the context section"):
            self.assertEqual(response.context['section'], 'pref')
        with self.subTest("A empty setting test"):
            self.assertEqual(response.context['object'].formal_preferences.get('preferred_tags').setting, [])
            self.assertTemplateUsed(response, 'users/settings.html')
        self.client.post(reverse("koocook_core:profile:pref"), {
            'preferences': json.dumps({"preferred_tags": [{"name":"Meat","label":{"name":"","level":1}}]})
        })
        response = self.client.get(reverse("koocook_core:profile:pref"))
        with self.subTest("A setting test"):
            self.assertEqual(self.kc_user.formal_preferences["preferred_tags"].setting[0]['name'],
                             "Meat")

    def test_follow(self):
        response = self.client.post(reverse('koocook_core:profile:follow'), {
            'followee_id': self.kc_user.id
        })
        with self.subTest("Following self"):
            self.assertEqual(response.status_code, 401)

        response = self.client.post(reverse('koocook_core:profile:follow'), {
            'followee_id': self.user2.koocookuser.id
        })
        with self.subTest("Following the other user"):
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["current"]["id"], self.user2.koocookuser.id)

    def test_following(self):
        response = self.client.get(reverse('koocook_core:profile:follow'))
        with self.subTest("Get all following users of a current user"):
            self.assertEqual(response.status_code, 200)
            self.assertTrue("current" not in response.json())

    def test_unfollow(self):
        response = self.client.post(reverse('koocook_core:profile:unfollow'), {
            'followee_id': self.user2.koocookuser.id
        })
        with self.subTest("Unfollowing the other user"):
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["current"]["id"], self.user2.koocookuser.id)

