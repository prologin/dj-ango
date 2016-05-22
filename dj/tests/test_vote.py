from django.core.urlresolvers import reverse
from django.test import Client

import dj.models
from dj.tests import BaseTestCase


class TestVote(BaseTestCase):
    def setUp(self):
        self.url = reverse('dj:vote')
        self.client = Client()
        self.users = [self.create_user('user{}'.format(i)) for i in range(5)]
        songs = [dj.models.Song(artist="Artist {}".format(i),
                                title="Title {}".format(i),
                                duration=60 + 60 * i,
                                path="/tmp/whatever{}.mp3".format(i))
                 for i in range(10)]
        dj.models.Song.objects.bulk_create(songs)
        self.songs = dj.models.Song.objects.all()

    def tearDown(self):
        self.client.logout()

    def data(self, song, action):
        return {
            'csrfmiddlewaretoken': self.client.cookies['csrftoken'].value,
            'next': self.url,
            'song_id': song.pk,
            'action': action,
        }

    def test_bad_action(self):
        self.login_user(self.users[0].username)
        self.client.get(self.url)
        response = self.client.post(self.url, self.data(self.songs[0], 'foo'))
        self.assertBadRequest(response)

    def test_add_remove_vote(self):
        song = self.songs[0]
        votes = 0
        self.assertEqual(song.votes.count(), votes)

        for user in self.users:
            self.login_user(user.username)
            self.client.get(self.url)
            response = self.client.post(self.url, self.data(song, 'add'))
            votes += 1
            self.assertRedirects(response, self.url)
            self.assertEqual(song.votes.count(), votes)

        for user in self.users:
            self.login_user(user.username)
            self.client.get(self.url)
            response = self.client.post(self.url, self.data(song, 'remove'))
            votes -= 1
            self.assertRedirects(response, self.url)
            self.assertEqual(song.votes.count(), votes)
