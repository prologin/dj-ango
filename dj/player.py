import contextlib
import logging
import random
import time

import mpd
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache

import dj.models

logger = logging.getLogger('dj.player')


@contextlib.contextmanager
def mpd_client():
    logger.debug("New connection to mpd")
    client = mpd.MPDClient()
    client.connect(*settings.MPD_ADDRESS)
    yield client
    client.disconnect()


def get_volume(cached=True) -> int:
    def volume():
        with mpd_client() as client:
            return int(client.status()['volume'])
    if cached:
        return cache.get_or_set('mpd/volume', volume, 10)
    else:
        return volume()


def set_volume(volume: int):
    volume = min(100, max(0, volume))
    with mpd_client() as client:
        client.setvol(volume)


def skip():
    with mpd_client() as client:
        client.next()


def main():
    state = dj.models.Player.objects.first()

    delay = 1

    def run(client):
        nonlocal delay

        while True:
            status = client.status()
            if client.playlist() and status['state'] == 'play':
                logger.info("Already playing, waiting for end")
                client.idle('playlist')
                logger.info("Song ended, requesting next")
            else:
                logger.info("Not playing, requesting next")
                client.clear()

            next_song = dj.models.Song.objects.first()
            if not next_song:
                raise ObjectDoesNotExist()

            delay = 1

            if next_song.votes.count() == 0:
                logger.debug("Not enough votes, choosing random next song")
                songs = dj.models.Song.objects.all()
                next_song = songs[random.randint(0, songs.count() - 1)]

            logger.info("Next song: %s (%s)", next_song, next_song.path)

            try:
                client.add(next_song.path)
            except mpd.CommandError:
                logger.warn("Song not found! Updating database")
                # File not found: database may not be up-to-date
                client.update()
                client.idle('update')
                client.idle('update')
                client.add(next_song.path)

            client.idle('playlist')  # consume playlist event
            client.play()
            next_song.votes.clear()
            next_song.save()
            state.set_next_song(next_song)
            state.save()
            state.refresh_from_db()

    while True:
        try:
            with mpd_client() as client:
                logger.debug("mpd version is %s", client.mpd_version)
                # Enable consume mode (played songs are deleted from playlist)
                client.consume(1)
                run(client)

        except ObjectDoesNotExist:
            logger.error("No song available; trying again in %.2f s", delay)

        except mpd.ConnectionError:
            logger.error("Connection error; trying again in %.2f s", delay)

        time.sleep(delay)
        delay *= 1.5


if __name__ == '__main__':
    main()
