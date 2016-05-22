from django.core.management import BaseCommand

from dj.player import main


class Command(BaseCommand):
    help = "Run the MPD player control"

    def handle(self, *args, **options):
        main()
