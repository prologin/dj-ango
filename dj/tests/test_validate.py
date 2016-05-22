from django.core.urlresolvers import reverse
from django.test import Client

from dj.templatetags.djutils import elapsed
from dj.tests import BaseTestCase
import dj.models


class TestValidate(BaseTestCase):
    def setUp(self):
        user = self.create_user('user')
        self.create_user('staff', is_staff=True)
        self.client = Client()
        self.url = reverse('dj:validate')
        self.artist = "Rick Astley"
        self.title = "Give you up"
        self.pending_song = dj.models.PendingSong(
            artist=self.artist, title=self.title, duration=1337,
            source="youtube", identifier="dQw4w9WgXcQ",
            submitter=user)
        self.pending_song.save()
        self.client.login(username='staff', password=self.DEFAULT_PASSWORD)

    def tearDown(self):
        dj.models.PendingSong.objects.all().delete()
        dj.models.Song.objects.all().delete()
        self.client.logout()

    def data(self, decision):
        return {
            'csrfmiddlewaretoken': self.client.cookies['csrftoken'].value,
            'decision': decision,
            'song_id': self.pending_song.pk,
            'artist': self.pending_song.artist,
            'title': self.pending_song.title,
        }

    def test_list(self):
        from dj.source.youtube import YouTube
        self.assertEqual(dj.models.PendingSong.objects.count(), 1)
        response = self.client.get(self.url)
        self.assertContains(response, self.artist, count=1)
        self.assertContains(response, self.title, count=1)
        self.assertContains(response, YouTube.source_name, count=1)
        self.assertContains(response, YouTube.get_url(self.pending_song.identifier), count=1)
        self.assertContains(response, "Nuke", count=1)
        self.assertContains(response, "Ban", count=1)
        self.assertContains(response, elapsed(self.pending_song.duration), count=1)

    def test_nuke(self):
        self.assertEqual(dj.models.PendingSong.objects.count(), 1)
        # Retrieve csrftoken
        self.client.get(self.url)
        response = self.client.post(self.url, self.data('nuke'))
        self.assertRedirects(response, self.url)
        self.assertEqual(dj.models.PendingSong.objects.count(), 0)

    def test_ban(self):
        self.assertEqual(dj.models.PendingSong.objects.count(), 1)
        # Retrieve csrftoken
        self.client.get(self.url)
        response = self.client.post(self.url, self.data('ban'))
        self.assertRedirects(response, self.url)
        self.assertEqual(dj.models.PendingSong.objects.count(), 1)
        self.assertEqual(dj.models.PendingSong.objects.filter(banned=True).count(), 1)

    def test_unban(self):
        self.assertEqual(dj.models.PendingSong.objects.count(), 1)
        # Retrieve csrftoken
        self.client.get(self.url)
        response = self.client.post(self.url, self.data('ban'))
        self.assertRedirects(response, self.url)
        self.assertEqual(dj.models.PendingSong.objects.count(), 1)
        self.assertEqual(dj.models.PendingSong.objects.filter(banned=True).count(), 1)
        response = self.client.post(self.url, self.data('unban'))
        self.assertRedirects(response, self.url)
        self.assertEqual(dj.models.PendingSong.objects.count(), 1)
        self.assertEqual(dj.models.PendingSong.objects.filter(banned=True).count(), 0)

    def test_validate(self):
        with self.settings(YOUTUBE_FAKE_DOWNLOAD=True):
            self.assertEqual(dj.models.PendingSong.objects.count(), 1)
            self.assertEqual(dj.models.Song.objects.count(), 0)
            # Retrieve csrftoken
            self.client.get(self.url)
            response = self.client.post(self.url, self.data('validate'))
            self.assertRedirects(response, self.url)
            self.assertEqual(dj.models.PendingSong.objects.count(), 0)
            self.assertEqual(dj.models.Song.objects.count(), 1)
