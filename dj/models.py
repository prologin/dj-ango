from django.conf import settings
from django.db import models
from django.utils import timezone
from django_prometheus.models import ExportModelOperationsMixin

SONG_SOURCES = [('youtube', "YouTube"), ]


class Song(ExportModelOperationsMixin('song'), models.Model):
    """
    Represents a validated song that can be played.
    """

    title = models.CharField(max_length=256, verbose_name="Song title")
    artist = models.CharField(max_length=256, verbose_name="Artist")
    path = models.FilePathField(verbose_name="Path to file", unique=True)
    duration = models.IntegerField(verbose_name="Duration in seconds")
    votes = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                   related_name='voted_songs',
                                   verbose_name="Votes by users",
                                   blank=True)

    def __str__(self):
        return "%s - %s" % (self.title, self.artist)


class PendingSong(ExportModelOperationsMixin('pending_song'), models.Model):
    """
    Represents a song waiting to be validated.
    """

    submitter = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  related_name='submitted_songs',
                                  verbose_name="Submitter")
    banned = models.BooleanField(
        default=False,
        verbose_name="Banned",
        help_text="Any further submissions of this song will be automatically nuked.")

    title = models.CharField(max_length=256, verbose_name="Song title")
    artist = models.CharField(max_length=256,
                              verbose_name="Song artist",
                              blank=True)
    source = models.CharField(max_length=16,
                              choices=SONG_SOURCES,
                              verbose_name="Source")
    link = models.CharField(max_length=64, verbose_name="Link")

    def __str__(self):
        return "%s - %s [%s]" % (self.title, self.artist, self.link)


class Player(models.Model):
    """
    Represents the state of the player.
    """

    song = models.ForeignKey(
        Song, verbose_name="Current song",
        null=True, blank=True)
    start_time = models.DateTimeField(
        verbose_name="Current song starting time",
        null=True,
        blank=True)
    volume = models.PositiveIntegerField(verbose_name="Current volume",
                                         null=True,
                                         blank=True)

    @classmethod
    def instance(cls):
        return cls.objects.first()

    def is_valid(self):
        return all(attr is not None
                   for attr in (self.song, self.start_time, self.volume))

    def set_next_song(self, song):
        self.song = song
        self.start_time = timezone.now()

    def __str__(self):
        return "Playing: %s" % self.song
