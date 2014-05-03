from mpd import MPDClient
from django.db.models import Count
from DJ_Ango.dj.models import *
import datetime
import time
import os
import os.path
import atexit

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
        self.client.setvol(vol)
      except Exception:
        self.client.connect("127.0.0.1", 4251)
        self.client.setvol(vol)
        self.client.disconnect()
    
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
        self.client.update()
        self.client.idle(["playlist"])
        self.client.idle(["playlist"])
        self.client.idle(["playlist"])
        song = player.song
        next = Song.objects.all().annotate(Count('votes')) \
            .order_by('-votes__count')[0]
        if self.client.playlist() != []:
          self.client.idle(["playlist"])
          self.client.clear()
        self.client.add(next.file)
        self.client.play()
        self.client.idle(["playlist"])
        self.client.idle(["playlist"])
        self.client.idle(["playlist"])
        next.votes = []
        next.save()
        player.song = next
        player.start_time = datetime.datetime.now()
        player.save()
        self.client.disconnect()
      self.client.close()
