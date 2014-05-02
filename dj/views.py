from django.views.decorators.csrf import csrf_protect
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.db.models import Count
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from DJ_Ango.dj.models import *
from DJ_Ango.dj.player import MPDPlayer
from apiclient.discovery import build
import DJ_Ango.dj.youtube as youtube
import threading
import math
import re

@csrf_protect
def index(request):
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
  if "volume" in request.POST and user.is_superuser:
    player = Player.objects.get(id=1)
    player.volume = request.POST["volume"]
    player.save()
    player = MPDPlayer()
    player.set_vol(request.POST["volume"])
  size_next = 5
  songs = Song.objects.all().annotate(Count('votes')).order_by('-votes__count')
  playing = Player.objects.get(id=1).song
  time = "%d:%02d" % divmod(playing.duration, 60)
  args = {'songs': songs[:size_next], 'playing': playing, 'time': time, 'user': user}
  if user.is_superuser:
    args["volume"] = Player.objects.get(id=1).volume
  return render_to_response('dj/index.html', args,
      context_instance=RequestContext(request))

class YTResult:
  def __init__(self, title, link):
    self.title = title
    self.link = link

def yt_search(search):
  yt = build('youtube', 'v3', developerKey='AIzaSyBj5jEAc9hqRzklXD6sO5dYqO0i9b34EBw')
  res = yt.search().list(q=search, maxResults=10, type="video", part="snippet").execute()
  return [YTResult(r["snippet"]["title"], r["id"]["videoId"]) for r in res["items"]]

@csrf_protect
def add(request):
  if not request.user.is_authenticated():
    return redirect('/login', prev=request.path)
  user = request.user
  results = None
  if "search" in request.POST:
    search = request.POST["search"]
    results = yt_search(search)
  if "link" in request.POST:
    artist = request.POST["artist"] if "artist" in request.POST else "Unknown"
    link = request.POST["link"] if "link" in request.POST else "Not given"
    if link and "?v=" in link:
      link = link.split("?v=")[1]      
    PendingSong(title=request.POST["title"], artist=artist, link=link, user=user).save()
  pending = PendingSong.objects.filter(user=user)
  args = {'pending': pending, 'user': user, 'results': results}
  return render_to_response('dj/add.html', args,
      context_instance=RequestContext(request))

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
  player = MPDPlayer()
  player.update()

@csrf_protect
def validate(request):
  if not (request.user.is_authenticated() and request.user.is_superuser):
    return redirect('/')
  user = request.user
  if "id" in request.POST and request.user.is_superuser:
    pending = PendingSong.objects.get(id=request.POST["id"])
    pending.title = request.POST["title"]
    pending.artist = request.POST["artist"] if "artist" in request.POST else "Unknown"
    pending.link = request.POST["link"]
    if request.POST["action"] == "validate":
      print("Downloading %s" % pending)
      threading.Thread(target=download_and_save, args=[pending]).start()
    pending.delete()
  pending = PendingSong.objects.all()
  return render_to_response('dj/validate.html', {'pending': pending},
      context_instance=RequestContext(request))

@csrf_protect
def vote(request, page):
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
  perpage = 10
  lastpage = math.ceil(Song.objects.count() / perpage)
  pages = 5
  page = max(0, min(lastpage, int(page)))
  if page <= pages // 2:
    start = 1
    end = min(pages, lastpage)
  elif page > lastpage - pages // 2:
    start = max(1, lastpage - pages + 1)
    end = lastpage
  else:
    start = page - pages // 2
    end = start + pages - 1
  songs = Song.objects.all().annotate(Count('votes')) \
      .order_by('-votes__count')[perpage*(page-1):perpage*page]
  args = {'page': page, 'perpage': perpage, 'last': lastpage, 'start': start,
      'end': end, 'range': range(start, end+1), 'songs': songs, 'user': user}
  return render_to_response('dj/vote.html', args,
      context_instance=RequestContext(request))

@csrf_protect
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
