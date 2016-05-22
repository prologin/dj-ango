from django.conf import settings
from django.db import models
from django.db.models import Count
from django.utils import timezone
from django.utils.functional import cached_property
from django_prometheus.models import ExportModelOperationsMixin

import dj.source
from dj.templatetags.djutils import elapsed


class BaseSong(models.Model):
    title = models.CharField(max_length=256, verbose_name="Title")
    artist = models.CharField(max_length=256,
                              verbose_name="Artist",
                              blank=True)
    duration = models.IntegerField(verbose_name="Duration",
                                   help_text="In seconds.")

    @cached_property
    def human_duration(self):
        return elapsed(self.duration)

    def __str__(self):
        return "{}{} ({})".format(self.artist + " – " if self.artist else "",
                                  self.title, elapsed(self.duration))

    class Meta:
        abstract = True


class SongManager(models.Manager):
    def get_queryset(self):
        return (super().get_queryset().annotate(vote_count=Count('votes'))
                .order_by('-vote_count', 'id'))


class Song(ExportModelOperationsMixin('song'), BaseSong):
    """
    Represents a validated song that can be played.
    """

    objects = SongManager()

    path = models.CharField(max_length=512,
                            verbose_name="Path to file",
                            unique=True)
    votes = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                   related_name='voted_songs',
                                   verbose_name="Votes by users",
                                   blank=True)


class PendingSong(ExportModelOperationsMixin('pending_song'), BaseSong):
    """
    Represents a song waiting to be validated.
    """

    submitter = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  on_delete=models.CASCADE,
                                  related_name='submitted_songs',
                                  verbose_name="Submitter")
    banned = models.BooleanField(
        default=False,
        verbose_name="Banned",
        help_text="Any further submissions of this song will be automatically nuked.")
    source = models.CharField(max_length=16, verbose_name="Source")
    identifier = models.CharField(max_length=256, verbose_name="Identifier")

    class Meta:
        ordering = ('banned', '-id')
        unique_together = ('source', 'identifier')

    @cached_property
    def url(self):
        return self.source_class().get_url(self.identifier)

    def source_class(self) -> dj.source.SongSource:
        return dj.source.from_code(self.source)


class Player(models.Model):
    """
    Represents the state of the player.
    """

    song = models.ForeignKey(Song,
                             on_delete=models.SET_NULL,
                             null=True,
                             blank=True,
                             verbose_name="Current song")
    start_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Current song starting time")

    @classmethod
    def instance(cls):
        return cls.objects.first()

    def is_playing(self):
        return all(attr is not None for attr in (self.song, self.start_time))

    def set_next_song(self, song):
        self.song = song
        self.start_time = timezone.now()

    def __str__(self):
        if self.is_playing():
            return "Playing: %s" % self.song
        else:
            return "Not playing"
