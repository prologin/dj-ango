from django.template import RequestContext
from django.core.paginator import Paginator
from django.shortcuts import render_to_response, redirect
from django.db.models import Count, Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.http import HttpResponse
from DJ_Ango.dj.models import *
from DJ_Ango.dj.player import MPDPlayer
from DJ_Ango.dj.utils import compute_time
from apiclient.discovery import build
import DJ_Ango.dj.youtube as youtube
import threading
import math
import re
import datetime

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
  playing = player.song
  elapsed = datetime.datetime.now() - player.start_time
  cm, cs = divmod(elapsed.seconds, 60)
  dm, ds = divmod(playing.duration, 60)
  time = "%d:%02d/%d:%02d" % (cm, cs, dm, ds)
  args = {'songs': songs[:size_next], 'playing': playing, 'time': time, 'user': user}
  if user.is_superuser:
    args["volume"] = Player.objects.get(id=1).volume
  return render_to_response(template, args,
      context_instance=RequestContext(request))

def now_playing(request):
  return index(request, "dj/now_playing.html")

def next(request):
  return index(request, "dj/next.html")

class YTResult:
  def __init__(self, title, link):
    self.title = title
    self.link = link

def yt_search(search):
  yt = build('youtube', 'v3', developerKey='AIzaSyBj5jEAc9hqRzklXD6sO5dYqO0i9b34EBw')
  res = yt.search().list(q=search, maxResults=10, type="video", part="snippet").execute()
  return [YTResult(r["snippet"]["title"], r["id"]["videoId"]) for r in res["items"]]

def add(request):
  if not request.user.is_authenticated():
    return redirect('/login', prev=request.path)
  user = request.user
  results = None
  if "search" in request.POST:
    search = request.POST["search"]
    if "?v=" in search:
      results = [YTResult("Direct link", search.split("?v=")[1])]
    else:
      results = yt_search(search)
  if "link" in request.POST:
    artist = request.POST["artist"] if "artist" in request.POST else "Unknown"
    link = request.POST["link"] if "link" in request.POST else "Not given"
    if link and "?v=" in link:
      link = link.split("?v=")[1]
    PendingSong(title=request.POST["title"], artist=artist, link=link, user=user).save()
  if "file" in request.FILES:
    save_upload(request.FILES["file"], request.POST["title"],
        request.POST["artist"] if "artist" in request.POST else None)
  pending = PendingSong.objects.filter(user=user)
  args = {'pending': pending, 'user': user, 'results': results}
  return render_to_response('dj/add.html', args,
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
  try:
    info = youtube.download_audio(pending.link)
  except:
    print("Couldn't download %s (%s)" % (pending.title, pending.link))
    return
  title = info["title"]
  artist = pending.artist
  if artist is None:
    artist = Artist.objects.get(name="Unknown")
  elif Artist.objects.filter(name=artist).exists():
    artist = Artist.objects.get(name=artist)
  else:
    artist = Artist(name=artist)
    artist.save()
  f = info["filename"]
  duration = info["duration"]
  Song(title=pending.title, artist=artist, file=f, duration=duration).save()

def validate(request):
  if not (request.user.is_authenticated() and request.user.is_superuser):
    return redirect('/')
  user = request.user
  if "id" in request.POST and request.user.is_superuser:
    pending = PendingSong.objects.get(id=request.POST["id"])
    pending.title = request.POST["title"]
    pending.artist = request.POST["artist"] if "artist" in request.POST else "Unknown"
    if pending.artist == "":
      pending.artist = "Unknown"
    pending.link = request.POST["link"]
    if request.POST["action"] == "validate":
      print("Downloading %s" % pending)
      threading.Thread(target=download_and_save, args=[pending]).start()
    pending.delete()
  pending = PendingSong.objects.all()
  return render_to_response('dj/validate.html', {'pending': pending},
      context_instance=RequestContext(request))

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
  args = {'page': p.page(page), 'num_pages': p.num_pages, 'category': category, 'user': user}
  return render_to_response(template, args,
      context_instance=RequestContext(request))

def vote_category(request, c, page):
  return vote(request, page, category=c)

def vote_get_category(request, c, page):
  return vote(request, page, "dj/vote_page.html", c)

def add_vote(request, song_id):
  song = Song.objects.get(id=song_id)
  song.votes.add(User.objects.get(username=request.user))
  song.save()
  return HttpResponse("OK")

def del_vote(request, song_id):
  song = Song.objects.get(id=song_id)
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
