from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase

User = get_user_model()


class BaseTestCase(TestCase):
    DEFAULT_PASSWORD = 'pswd'

    def create_user(self, username, **kwargs):
        return User.objects.create_user(username=username,
                                        email='username@example.org',
                                        password=BaseTestCase.DEFAULT_PASSWORD,
                                        **kwargs)

    def login_user(self, username):
        self.client.login(username=username,
                          password=BaseTestCase.DEFAULT_PASSWORD)

    def assertGetRedirectsNext(self, url_name):
        url = reverse(url_name)
        response = self.client.get(url)
        self.assertRedirects(response,
                             '{}?next={}'.format(settings.LOGIN_URL, url))

    def assertStatus(self, response, status):
        if callable(status):
            self.assertTrue(status(response.status_code))
        else:
            self.assertEqual(response.status_code, status)

    def assertOk(self, response):
        return self.assertStatus(response, lambda sc: 200 <= sc < 300)

    def assertBadRequest(self, response):
        return self.assertStatus(response, 400)

    def assertForbidden(self, response):
        return self.assertStatus(response, 403)
