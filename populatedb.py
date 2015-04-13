#! /usr/bin/env python3

import sys
sys.path.append("/var/django")
import settings
from dj.models import *
import django
from django.contrib.auth.models import User
import os
import os.path
import re
import smtplib
from hsaudiotag import auto
from hashlib import md5

#if len(sys.argv) < 2:
#  print("usage: %s directory" % sys.argv[0])
#  sys.exit(1)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

#with open("paralleles2017") as passwd:
#  for l in passwd.read().split("\n"):
#    if l != "":
#      user = l
#      password = md5(("lol" + l).encode("ascii")).hexdigest()[-6:]
#      print("%s %s" % (user, password))
#      try:
#        new = User.objects.create_user(user, user + "@epita.fr", password)
#        new.save()
#      except:
#        pass

lost = []
with open("lostfiles") as f:
  for l in f:
    elts = l[:-1].split(";")
    artist = elts[0]
    if artist == "":
      print("Void artist:", l)
    title = elts[1]
    if title == "":
      print("Void title:", l)
    path = ";".join(elts[2:])
    if path == "":
      print("Void path:", l)
    lost.append((artist, title, path))

for a, t, p in lost:
  if Artist.objects.filter(name=a).exists():
    artist = Artist.objects.get(name=a)    
  else:
    artist = Artist(name=a)
    artist.save()
  fname = p[len("dj/songs/"):]
  duration = auto.File(p).duration
  song = Song(title=t, artist=artist, file=fname, duration=duration)
  #song.save()
  print("Added %s - %s (%s) (%ds)" % (artist.name, t, fname, duration))
print("Done.")
