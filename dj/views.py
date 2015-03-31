from django.template import RequestContext
from django.core.paginator import Paginator
from django.shortcuts import render_to_response, redirect
from django.db.models import Count, Q
from dj.models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.http import HttpResponse
from dj.player import MPDPlayer
from dj.utils import compute_time
from apiclient.discovery import build
import dj.youtube as youtube
import dj.groove as groove
import urllib.parse as url
import threading
import math
import re
import os
import datetime

def sec2str(sec):
  m, s = divmod(sec, 60)
  return "%d:%02d" % (m, s)

def index(request, template="dj/index.html"):
  if not request.user.is_authenticated():
    return redirect('/login', prev=request.path)
  user = request.user
  if "todo" in request.POST and "id" in request.POST:
    todo = request.POST["todo"]
    if todo == "add":
      song = Song.objects.get(id=request.POST["id"])
      song.votes.add(User.objects.get(username=user))
    elif todo == "remove":
      song = Song.objects.get(id=request.POST["id"])
      song.votes.remove(User.objects.get(username=user))
  player = Player.objects.get(id=1)
  if "volume" in request.POST and user.is_superuser:
    player.volume = request.POST["volume"]
    player.save()
    mpdplayer = MPDPlayer()
    mpdplayer.set_vol(request.POST["volume"])
  size_next = 5
  songs = Song.objects.all().annotate(Count('votes')).order_by('-votes__count')
  songs = songs[:size_next]
  for s in songs:
    setattr(s, 'time', sec2str(s.duration))
  playing = player.song
  elapsed = datetime.datetime.now() - player.start_time
  cm, cs = divmod(elapsed.seconds, 60)
  dm, ds = divmod(playing.duration, 60)
  time = "%d:%02d/%d:%02d" % (cm, cs, dm, ds)
  args = {'songs': songs, 'playing': playing, 'time': time, 'user': user}
  if user.is_superuser:
    args["volume"] = Player.objects.get(id=1).volume
  return render_to_response(template, args,
      context_instance=RequestContext(request))

def now_playing(request):
  return index(request, "dj/now_playing.html")

def next(request):
  return index(request, "dj/next.html")

class Result:
  def __init__(self, title, link, duration, source="youtube"):
    self.title = title
    self.link = link
    self.duration = duration
    self.source = source

class Results:
  def __init__(self, site, results):
    self.site = site
    self.results = results

def pt2str(t):
  s = t[2:-1]
  m, s = s.split("M") if "M" in s else ("0" , s)
  if len(s) == 1:
    s = '0' + s
  return m + ":" + s

def yt_search(search):
  yt = build('youtube', 'v3', developerKey='AIzaSyBj5jEAc9hqRzklXD6sO5dYqO0i9b34EBw')
  res = yt.search().list(q=search, maxResults=10, type="video", part="id,snippet").execute()
  ids = ",".join(r["id"]["videoId"] for r in res["items"])
  res = yt.videos().list(id=ids, part='id,snippet,contentDetails').execute()
  for r in res["items"]:
    r["len"] = pt2str(r["contentDetails"]["duration"])
  url = "https://www.youtube.com/watch?v="
  return [Result(r["snippet"]["title"], url + r["id"],  r["len"]) for r in res["items"]]

def gs_search(search):
  ret = []
  for s in groove.searchSong(search):
    try:
      duration = sec2str(int(s["EstimateDuration"].split(".")[0]))
      source = "grooveshark-" + s["SongID"] + "-" + s["ArtistID"]
      p = Result(s["ArtistName"] + " - " + s["SongName"], "", duration, source)
      ret.append(p)
    except Exception as e:
      print("gs_search")
      print(e)
  return ret

def add(request):
  if not request.user.is_authenticated():
    return redirect('/login', prev=request.path)
  user = request.user
  results = None
  pending = PendingSong.objects.filter(user=user)
  args = {'pending': pending, 'user': user, 'results': None}
  return render_to_response('dj/add.html', args,
      context_instance=RequestContext(request))

def add_results(request, search):
  user = request.user
  if not user.is_authenticated():
    return HttpResponse("You need to be connected")
  results = []
  if "?v=" in search:
    results.append(Results("Youtube", [Result("Direct link", search)]))
  else:
    results.append(Results("Grooveshark", gs_search(search)))
    results.append(Results("Youtube", yt_search(search)))
  pending = PendingSong.objects.filter(user=user)
  args = {'pending': pending, 'user': user, 'results': results}
  return render_to_response('dj/add_search.html', args,
      context_instance=RequestContext(request))

def add_pending(request):
  try:
    artist = request.POST["artist"] if "artist" in request.POST else "Unknown"
    if "link" in request.POST:
      if request.POST["link"] == "" and request.POST["source"].startswith("grooveshark"):
        token = groove.getTokenForSong(request.POST["source"].split("-")[1])
        link = "http://grooveshark.com/#!/s/" + url.quote_plus(request.POST["title"]) + "/" + token
      else:
        link = request.POST["link"] if request.POST["link"] != "" else "Not given"
    src = request.POST["source"] if "source" in request.POST else "?"
    PendingSong(title=request.POST["title"], artist=artist, link=link, src=src, user=request.user).save()
    return HttpResponse("OK")
  except Exception as e:
    print("add_pending")
    print(e)

def add_upload(request):
  save_upload(request.FILES["file"], request.POST["title"],
      request.POST["artist"] if "artist" in request.POST else None)
  return redirect("/add")

def user_pending(request):
  user = request.user
  if not user.is_authenticated():
    return HttpResponse("You need to be connected")
  pending = PendingSong.objects.filter(user=user)
  args = {'pending': pending}
  return render_to_response('dj/add_pending.html', args,
      context_instance=RequestContext(request))

def save_upload(f, title, artist):
  ext = "." + str(f).split(".")[-1]
  fname = ((artist + " - ") if artist else "") + title + ext
  path = "/var/django/DJ_Ango/dj/songs/upload/"
  with open(path + fname, "wb+") as dst:
    for c in f.chunks():
      dst.write(c)
  if artist is None:
    artist = Artist.objects.get(name="Unknown")
  elif Artist.objects.filter(name=artist).exists():
    artist = Artist.objects.get(name=artist)
  else:
    artist = Artist(name=artist)
    artist.save()
  duration = compute_time(f)
  Song(title=title, artist=artist, file=("upload/" + fname), duration=duration).save()

def download_and_save(pending):
  print("Downloading %s" % pending)
  if pending.src == "youtube":
    yt_dl(pending)
  elif pending.src.startswith("grooveshark"):
    gs_dl(pending)

def yt_dl(pending):
  try:
    info = youtube.download_audio(pending.link)
  except:
    print("Couldn't download %s (%s)" % (pending.title, pending.link))
    return
  artist = pending.artist
  if artist is None:
    artist = Artist.objects.get(name="Unknown")
  elif Artist.objects.filter(name=artist).exists():
    artist = Artist.objects.get(name=artist)
  else:
    artist = Artist(name=artist)
    artist.save()
  f = "youtube/" + info["filename"]
  duration = info["duration"]
  Song(title=pending.title, artist=artist, file=f, duration=duration).save()

def gs_dl(pending):
  print("src: " + pending.src)
  sid, aid = pending.src.split("-")[1:3]
  path = "dj/songs/grooveshark/"
  f = groove.downloadSong(sid, aid, pending.title, pending.artist, path)
  if not os.path.isfile(path + f):
    return
  artist = pending.artist
  if artist is None:
    artist = a if a != "" else Artist.objects.get(name="Unknown")
  elif Artist.objects.filter(name=artist).exists():
    artist = Artist.objects.get(name=artist)
  else:
    artist = Artist(name=artist)
    artist.save()
  duration = compute_time(path + f)
  f = "grooveshark/" + f
  Song(title=pending.title, artist=artist, file=f, duration=duration).save()

def validate(request, template='dj/validate.html'):
  if not (request.user.is_authenticated() and request.user.is_superuser):
    return redirect('/')
  pending = PendingSong.objects.all()
  return render_to_response(template, {'pending': pending},
      context_instance=RequestContext(request))

def pending(request):
  return validate(request, 'dj/pending.html')

def validate_pending(request, i):
  user = request.user
  if request.user.is_superuser:
    pending = PendingSong.objects.get(id=i)
    pending.title = request.POST["title"]
    pending.artist = request.POST["artist"] if "artist" in request.POST else "Unknown"
    if pending.artist == "":
      pending.artist = "Unknown"
    pending.link = request.POST["link"]
    threading.Thread(target=download_and_save, args=[pending]).start()
    pending.delete()
    return HttpResponse("OK")
  else:
    return HttpResponse("Admin only, GTFO.")

def nuke_pending(request, i):
  user = request.user
  if request.user.is_superuser:
    PendingSong.objects.get(id=i).delete()
    return HttpResponse("OK")
  else:
    return HttpResponse("Admin only, GTFO.")

def vote(request, page, template="dj/vote.html", category="all"):
  if not request.user.is_authenticated():
    return redirect('/login', prev=request.path)
  user = request.user
  if "search" in request.POST:
    search = request.POST["search"]
    songs = Song.objects\
        .filter(Q(title__icontains=search) | Q(artist__name__icontains=search))\
        .annotate(Count('votes')).order_by('-votes__count')
  elif category != "all":
    songs = Song.objects.all().filter(file__startswith=(category + "/"))\
            .annotate(Count('votes')).order_by('-votes__count')
  else:
    songs = Song.objects.all().annotate(Count('votes')).order_by('-votes__count')
  p = Paginator(songs, 100 if "search" in request.POST else 20)
  page = p.page(page)
  for s in page:
    setattr(s, 'time', sec2str(s.duration))
  args = {'page': page, 'num_pages': p.num_pages, 'category': category, 'user': user}
  return render_to_response(template, args,
      context_instance=RequestContext(request))

def vote_category(request, c, page):
  return vote(request, page, category=c)

def vote_get_category(request, c, page):
  return vote(request, page, "dj/vote_page.html", c)

def add_vote(request):
  if not "song_id" in request.POST:
    return HttpResponse("Nothing to do.")
  song = Song.objects.get(id=int(request.POST["song_id"]))
  song.votes.add(User.objects.get(username=request.user))
  song.save()
  return HttpResponse("OK")

def del_vote(request):
  if not "song_id" in request.POST:
    return HttpResponse("Nothing to do.")
  song = Song.objects.get(id=int(request.POST["song_id"]))
  song.votes.remove(User.objects.get(username=request.user))
  song.save()
  return HttpResponse("OK")

def login(request, prev='/'):
  if request.user.is_authenticated():
    return redirect('/logout')
  if "login" in request.POST and "password" in request.POST:
    user = authenticate(username=request.POST["login"],
                    password=request.POST["password"])
    if user is not None:
      auth_login(request, user)
      return redirect(prev)
  user = request.user.username
  return render_to_response('dj/login.html', {'user': user},
      context_instance=RequestContext(request))

def logout(request):
  auth_logout(request)
  return redirect('/login')
