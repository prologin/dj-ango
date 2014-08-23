#! /usr/bin/env python3

import sys
sys.path.append("/var/django")
from django.core.management import setup_environ
import settings
from dj.models import *
from django.contrib.auth.models import User
import os
import os.path
from hsaudiotag import auto

#if len(sys.argv) < 2:
#  print("usage: %s directory" % sys.argv[0])
#  sys.exit(1)

setup_environ(settings)

#with open("newpasswd") as passwd:
#  for l in passwd.read().split("\n"):
#    if l != "":
#      user, password = l.split(":")
#      print("user: %s, pass: %s" % (user, password))
#      new = User.objects.create_user(user, user + "@epita.fr", password)
#      new.save()

for s in Song.objects.all():
  if not (s.file.endswith(".mp3") or s.file.endswith(".m4a")):
    print(s.file)
    os.rename("dj/songs/" + s.file, "dj/songs/" + s.file + ".mp3")
    s.file = s.file + ".mp3"
    s.save()

#for fname in os.listdir(sys.argv[1]):
#  if not os.path.isfile(os.path.join(sys.argv[1], fname)):
#    continue
#  name = ".".join(fname.split(".")[:-1])
#  sp = name.split(" - ") 
#  if len(sp) > 1:
#    if Artist.objects.filter(name=sp[0]).exists():
#      artist = Artist.objects.get(name=sp[0])    
#    else:
#      artist = Artist(name=sp[0])
#      artist.save()
#    title = sp[1]
#  else:
#    artist = Artist.objects.get(name="Unknown")
#    title = sp[0]
#  duration = auto.File(os.path.join(sys.argv[1], fname)).duration
#  fname = "grooveshark/" + fname
#  song = Song(title=title, artist=artist, file=fname, duration=duration)
#  song.save()
#  print("Added %s - %s (%s) (%ds)" % (title, artist.name, fname, duration))
print("Done.")
