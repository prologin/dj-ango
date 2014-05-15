from DJ_Ango.dj.models import *
from django.contrib import admin

for mod in (Artist, Song, PendingSong, Player):
    admin.site.register(mod)
