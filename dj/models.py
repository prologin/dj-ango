from django.contrib.auth import models as auth
from django.db import models

class Artist(models.Model):
    """
    A song artist.
    """

    name = models.CharField(max_length=256, verbose_name='Artist name')

    def __str__(self):
        return self.name

class Song(models.Model):
    """
    Represents a music song which can be played.
    """

    title = models.CharField(max_length=256, verbose_name='Song title')
    artist = models.ForeignKey(Artist, verbose_name='Artist')
    file = models.CharField(max_length=512, verbose_name='Path to file')
    duration = models.IntegerField(verbose_name='Duration in seconds')
    votes = models.ManyToManyField(auth.User, verbose_name='Votes by users', blank=True)

    def __str__(self):
        return '%s (%s)' % (self.title, self.artist)

class PendingSong(models.Model):
    """
    Represents a youtube song waiting to be validated.
    """

    title = models.CharField(max_length=256, verbose_name='Song title')
    artist = models.CharField(max_length=256, verbose_name='Song artist')
    link = models.CharField(max_length=64, verbose_name='Youtube link')
    user = models.ForeignKey(auth.User, verbose_name="Submitter")

    def __str__(self):
        return '%s (%s) [%s]' % (self.title, self.artist, self.link)

class Player(models.Model):
    """
    Represents the state of the player
    """

    song = models.ForeignKey(Song, verbose_name="Current song")
    start_time = models.DateTimeField(verbose_name="Current song starting time")
    volume = models.PositiveIntegerField(verbose_name="Current volume")

    def __str__(self):
      return 'Playing: %s' % self.song
