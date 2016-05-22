from django.contrib.auth import get_user
from django.core.urlresolvers import reverse
from django.test.client import Client

from dj.tests import BaseTestCase


class TestPermissions(BaseTestCase):
    def setUp(self):
        self.client = Client()
        self.create_user('root', is_superuser=True, is_staff=True)
        self.create_user('staff', is_staff=True)
        self.create_user('user')

    def test_superuser_staff(self):
        self.assertTrue(self.client.login(username='root', password=self.DEFAULT_PASSWORD))
        self.assertTrue(get_user(self.client).is_superuser)

        self.assertTrue(self.client.login(username='staff', password=self.DEFAULT_PASSWORD))
        self.assertFalse(get_user(self.client).is_superuser)
        self.assertTrue(get_user(self.client).is_staff)

        self.assertTrue(
            self.client.login(username='user', password=self.DEFAULT_PASSWORD))
        self.assertFalse(get_user(self.client).is_superuser)
        self.assertFalse(get_user(self.client).is_staff)

    def test_needs_login(self):
        pages = ('home', 'vote', 'suggest', 'validate', 'volume', 'skip',
                 'stub-now-playing', 'stub-playing-next')

        for page in pages:
            self.assertGetRedirectsNext('dj:' + page)

    def test_logged_in(self):
        pages = (
        'home', 'vote', 'suggest', 'stub-now-playing', 'stub-playing-next')

        self.client.login(username='user', password=self.DEFAULT_PASSWORD)
        for page in pages:
            self.assertOk(self.client.get(reverse('dj:' + page)))

    def test_needs_staff(self):
        pages = ('validate',)

        self.client.login(username='user', password=self.DEFAULT_PASSWORD)
        for page in pages:
            self.assertGetRedirectsNext('dj:' + page)

        self.client.login(username='staff', password=self.DEFAULT_PASSWORD)
        for page in pages:
            self.assertOk(self.client.get(reverse('dj:' + page)))
