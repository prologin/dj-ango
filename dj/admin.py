from dj.models import *
from django.contrib import admin


class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'duration')
    list_per_page = 2500
    search_fields = ('title', 'artist__name')


admin.site.register(Song, SongAdmin)

for mod in (PendingSong, Player):
    admin.site.register(mod)
