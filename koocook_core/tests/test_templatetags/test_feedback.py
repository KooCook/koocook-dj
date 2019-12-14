from django.http import HttpRequest
from django.shortcuts import reverse
from datetime import datetime
from koocook_core.views.feedback import post_feedback
from koocook_core.models import Author, Feedback
from koocook_core.tests.base import AuthTestCase
from koocook_core.views.forms.feedback import FeedbackForm


class FeedbackTest(AuthTestCase):
    model = Feedback
    form = FeedbackForm()

    def setUp(self) -> None:
        super().setUp()
        request = HttpRequest()
        request.user = self.user
        self.post = post_feedback(request)

    def test_create_feedback_without_image_vdo(self):
        self.model.objects.create(author=Author.objects.get(user__user=self.user),
                                  subject='test', body="It's a testing.")
        with self.subTest():
            self.assertEqual(self.model.objects.get(subject='test').body, "It's a testing.")
            self.assertIsNone(self.model.objects.get(subject='test').image)
            self.assertIsNone(self.model.objects.get(subject='test').video)

    def test_load_form(self):
        response = self.client.get(reverse('koocook_core:feedback'))
        with self.subTest():
            self.assertEqual(list(map(lambda x: str(x), response.context['form'])),
                             list(map(lambda x: str(x), self.form)))
            self.assertEqual(response.status_code, 200)

    def test_post_image(self):
        self.model.objects.create(author=Author.objects.get(user__user=self.user),
                                  subject='test', body="It's a testing.",
                                  image=["https://testing.com/testing-link.jpg"])
        self.assertEqual(self.model.objects.get(subject='test').image_tag(),
                         u'<img src=%s style="width: 80vw; height: auto; margin-bottom: 12px;"/>'
                         % self.model.objects.get(subject='test').image[0])

    def test_post_two_images(self):
        self.model.objects.create(author=Author.objects.get(user__user=self.user),
                                  subject='test', body="It's a testing.",
                                  image=["https://testing.com/testing-link.jpg",
                                         "https://testing.com/testing-link.jpg"])
        result = u''
        for i in range(len(self.model.objects.get(subject='test').image)):
            result += u'<img src=%s style="width: 80vw; height: auto; margin-bottom: 12px;"/>' %\
                     self.model.objects.get(subject='test').image[i]
        self.assertEqual(self.model.objects.get(subject='test').image_tag(), result)

    def test_post_video(self):
        self.model.objects.create(author=Author.objects.get(user__user=self.user),
                                  subject='test', body="It's a testing.",
                                  video="https://testing.com/testing-link.jpg")
        self.assertEqual(self.model.objects.get(subject='test').video_tag(),
                         u'<iframe src=%s width=80vw height=auto style="margin-bottom: 12px;"></iframe>'
                         % self.model.objects.get(subject='test').video)

    def test_finished_form(self):
        data = {'author': self.user, 'subject': 'test',
                'date_published': datetime.now(),
                'body': 'This is a test.',
                'image': ["https://testing.com/testing-link.jpg", "https://testing.com/testing-link.jpg"],
                'video': "https://testing.com/testing-link.jpg",
                'status': False}
        form = FeedbackForm(data=data)
        self.assertTrue(form.is_valid())

    def test_valid_form_without_image_video(self):
        data = {'author': self.user, 'subject': 'test',
                'body': 'This is a test.',
                }
        form = FeedbackForm(data=data)
        self.assertTrue(form.is_valid())
