from django.shortcuts import reverse
from django.test import TestCase


class BasicViewTest(TestCase):
    def test_home_page_view(self):
        response = self.client.get(reverse('koocook_core:index'))
        with self.subTest():
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, "index.html")
