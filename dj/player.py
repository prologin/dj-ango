import contextlib
import logging
import random

from django.conf import settings
from django.db.models import Count
from mpd import MPDClient

import dj.models

logger = logging.getLogger('dj.player')


class _Player:
    def __init__(self):
        self.should_stop = False

    def set_volume(self, volume):
        with self.client() as client:
            client.setvol(int(volume))

    def stop(self):
        self.should_stop = True

    @contextlib.contextmanager
    def client(self):
        client = MPDClient()
        client.connect(*settings.MPD_ADDRESS)
        yield client
        client.disconnect()

    def player_thread(self):
        state = dj.models.Player.objects.first()

        with self.client() as client:
            client.consume(1)

        while not self.should_stop:
            with self.client() as client:
                playlist = client.playlist()
                logger.debug("Playlist: %s", playlist)
                if playlist:
                    # end of song
                    client.idle("playlist")
                    client.clear()

            next = (dj.models.Song.objects.annotate(vote_count=Count('votes'))
                    .order_by('-vote_count', 'id'))[0]

            if next.votes.count() == 0:
                # not enough votes, choose randomly
                songs = dj.models.Song.objects.all()
                next = songs[random.randint(0, songs.count() - 1)]

            logger.debug("Next song: %s (%s)", next.file, next)

            with self.client() as client:
                try:
                    client.add(next.file)
                except Exception:
                    client.update()
                    client.idle("update")  # start
                    client.idle("update")  # end
                    client.add(next.file)
                client.play()
                next.votes.clear()
                next.save()
                state.set_next_song(next)
                state.save()
                state.refresh_from_db()


def player():
    if not hasattr(player, 'instance'):
        player.instance = _Player()
    return player.instance
