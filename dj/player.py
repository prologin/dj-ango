from mpd import MPDClient
from django.db.models import Count
from DJ_Ango.dj.models import *
import datetime
import time
import os
import os.path
import atexit
import random

class MPDPlayer:
  instance = None

  def __init__(self):
    if not MPDPlayer.instance:
      MPDPlayer.instance = MPDPlayer.__Player()

  def __getattr__(self, name):
    return getattr(self.instance, name)

  class __Player:
    def __init__(self):
      self.client = MPDClient()
      self.should_stop = False
      atexit.register(os.remove, "running")

    def set_vol(self, vol):
      try:
        self.client.setvol(int(vol))
      except:
        print("Could not set volume.")

    def stop(self):
      self.should_stop = True

    def player_thread(self):
      if os.path.isfile("running"):
        return
      open("running", "w+")
      time.sleep(2)
      player = Player.objects.all().get(id=1)
      self.client = MPDClient()
      self.client.connect("127.0.0.1", 4251)
      self.client.consume(1)
      self.client.disconnect()
      while not self.should_stop:
        self.client.connect("127.0.0.1", 4251)
        song = player.song
        if self.client.playlist() != []:
          self.client.idle(["playlist"]) #end of song
          self.client.clear()
        next = Song.objects.all().annotate(Count('votes')) \
            .order_by('-votes__count')[0]
        if next.votes.count() == 0:
          next = random.choice(Song.objects.all())
        try:
          self.client.add(next.file)
        except:
          self.client.update()
          self.client.idle(["update"]) #start
          self.client.idle(["update"]) #end
          self.client.add(next.file)
        self.client.play()
        self.client.idle(["playlist"]) #add
        self.client.idle(["playlist"]) #add is sending 2 events
        self.client.idle(["playlist"]) #play
        next.votes = []
        next.save()
        player.song = next
        player.start_time = datetime.datetime.now()
        player.save()
        self.client.disconnect()
      self.client.close()
