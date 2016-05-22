from dj.models import *
from django.contrib import admin


class SongMixin:
    list_display = ('title', 'artist', 'human_duration',)
    search_fields = ('title', 'artist',)

    def human_duration(self, obj):
        return obj.human_duration
    human_duration.admin_order_field = 'duration'


class SongAdmin(SongMixin, admin.ModelAdmin):
    list_display = SongMixin.list_display + ('vote_count',)
    exclude = ('votes',)

    def vote_count(self, obj):
        return obj.vote_count
    vote_count.short_description = "Vote count"
    vote_count.admin_order_field = 'vote_count'


class PendingSongAdmin(SongMixin, admin.ModelAdmin):
    list_display = SongMixin.list_display + ('submitter', 'banned',)
    search_fields = SongMixin.search_fields + ('submitter__username',)
    list_filter = ('source', 'banned', 'submitter',)

    # FIXME: filter submitter does not work for some reason
    # FIXME: display human name (not code) for source


admin.site.register(Song, SongAdmin)
admin.site.register(PendingSong, PendingSongAdmin)
admin.site.register(Player)
