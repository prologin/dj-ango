from django.core.urlresolvers import reverse
from django.test import Client
from django.utils.http import urlencode

import dj.models
from dj.tests import BaseTestCase


class TestSuggest(BaseTestCase):
    def setUp(self):
        self.create_user('user', is_staff=True)
        self.client = Client()
        self.client.login(username='user', password=self.DEFAULT_PASSWORD)

    def tearDown(self):
        dj.models.PendingSong.objects.all().delete()
        dj.models.Song.objects.all().delete()
        self.client.logout()

    def test_submit(self):
        from dj.source.youtube import YouTube

        url = reverse('dj:suggest')
        query = "Rick Astley - Never Gonna Give You Up"
        full_url = '{}?{}'.format(url, urlencode({'q': query}, doseq=True))

        response = self.client.get(full_url)
        self.assertContains(response, "Rick Astley", count=5 * 2 + 1)

        result = YouTube.search(query)[0]
        data = {
            'csrfmiddlewaretoken': self.client.cookies['csrftoken'].value,
            'artist': "The artist", 'title': "The title",
            'state': result.dump(),
        }

        # First suggestion is OK
        self.assertEqual(dj.models.PendingSong.objects.count(), 0)
        response = self.client.post(full_url, data, follow=True)

        self.assertContains(response, "was added to validation queue")
        self.assertEqual(dj.models.PendingSong.objects.count(), 1)

        # Try suggesting the same one
        response = self.client.post(full_url, data, follow=True)

        self.assertContains(response, "already pending validation")
        self.assertEqual(dj.models.PendingSong.objects.count(), 1)

        # Try suggesting a banned song
        pending_song = dj.models.PendingSong.objects.get()
        pending_song.banned = True
        pending_song.save()
        response = self.client.post(full_url, data, follow=True)

        self.assertContains(response, "banned from suggestions")
        self.assertEqual(dj.models.PendingSong.objects.count(), 1)
