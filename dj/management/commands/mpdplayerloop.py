from django.core.management import BaseCommand

from dj.player import mpd_player_loop


class Command(BaseCommand):
    help = "Run the mpd player loop"

    def handle(self, *args, **options):
        mpd_player_loop()
