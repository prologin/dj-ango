#! /usr/bin/env python3

import sys
sys.path.append("/var/django")
from django.core.management import setup_environ
import settings
from dj.models import *
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

setup_environ(settings)

with open("paralleles2017") as passwd:
  for l in passwd.read().split("\n"):
    if l != "":
      user = l
      password = md5(("lol" + l).encode("ascii")).hexdigest()[-6:]
      print("%s %s" % (user, password))
#      try:
#        new = User.objects.create_user(user, user + "@epita.fr", password)
#        new.save()
#      except:
#        pass

#for s in Song.objects.all():
#  try:
#    open(os.path.join("dj/songs", s.file)).close()
#  except:
#    print("Couldn't find file {}.".format(s.file))

#for fname in os.listdir(sys.argv[1]):
#  if not os.path.isfile(os.path.join(sys.argv[1], fname)):
#    continue
#  name = ".".join(fname.split(".")[:-1])
#  sp = re.split(" *--* *", name) 
#  if len(sp) > 1:
#    a, t = sp[0], " ".join(sp[1:])
#    if Artist.objects.filter(name=a).exists():
#      artist = Artist.objects.get(name=a)    
#    else:
#      artist = Artist(name=a)
#      artist.save()
#  else:
#    artist = Artist.objects.get(name="Unknown")
#    t = name
#  duration = auto.File(os.path.join(sys.argv[1], fname)).duration
#  fname = "ma/" + fname
#  song = Song(title=t, artist=artist, file=fname, duration=duration)
#  song.save()
#  print("Added %s - %s (%s) (%ds)" % (artist.name, t, fname, duration))
print("Done.")
