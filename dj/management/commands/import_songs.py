import argparse
import fnmatch
import mutagen
import os

from django.core.management import BaseCommand
from django.db import IntegrityError

import dj.models


class Command(BaseCommand):
    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument('directory',
                            nargs='+',
                            help="Directories to scan recursively")
        parser.add_argument('-i',
                            '--include',
                            default='*.mp3',
                            help="Glob pattern of files to import")
        parser.add_argument(
            '-a',
            '--all',
            action='store_true',
            help="Import files that have to metadata (use filename as title and no artist)")

    def handle(self, *args, **options):
        import_all = options['all']
        verbose = options['verbosity'] >= 2

        def analyse(path):
            if verbose:
                self.stdout.write(path)
            audio = mutagen.File(path, easy=True)
            title = ''
            artist = ''
            duration = None
            if audio is not None:
                try:
                    title = audio['title'][0]
                except (KeyError, IndexError):
                    pass
                try:
                    artist = ', '.join(audio['artist'])
                except KeyError:
                    pass
                duration = audio.info.length

            if not duration:
                if verbose:
                    self.stderr.write("\tno duration; skipped")
                return

            if not title:
                if not import_all and verbose:
                    self.stderr.write("\tno metadata; skipped")
                    return
                elif import_all:
                    title = os.path.splitext(os.path.basename(path))[0]
                    if verbose:
                        self.stderr.write(
                            "\tNo metadata; importing anyway (--all)")

            if verbose:
                self.stdout.write("\t{:<32} - {:<32}".format(title[:32],
                                                             artist[:32]))

            song = dj.models.Song(title=title,
                                  artist=artist,
                                  duration=duration,
                                  path=path)
            try:
                song.save()
            except IntegrityError:
                if verbose:
                    self.stderr.write("\tpath already in database")

        for directory in options['directory']:
            for root, dirs, files in os.walk(directory, followlinks=True):
                for file in files:
                    if fnmatch.fnmatch(file, options['include']):
                        analyse(os.path.join(root, file))
