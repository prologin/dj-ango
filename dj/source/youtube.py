import logging
import os.path

import isodate
import youtube_dl
from django.conf import settings
from django.core.cache import cache
from googleapiclient import discovery

from dj.source import SongSource, DataEncodedImage

logger = logging.getLogger('dj.source.youtube')


class YouTube(SongSource):
    source_name = "YouTube"
    source_icon = "youtube-play"

    url = 'https://youtube.com/watch?v={}'

    def __init__(self, data):
        snippet = data['snippet']
        details = data['contentDetails']
        self.title = snippet['title']
        self.artist = None
        if "-" in self.title:
            self.artist, self.title = map(str.strip, self.title.split('-', 1))
        self.description = snippet['description']
        self.tags = snippet.get('tags', [])
        self.date_published = isodate.parse_datetime(snippet['publishedAt'])
        self.duration = int(
            isodate.parse_duration(details['duration']).total_seconds())
        self.id = data['id']
        self.thumbnails = {
            name: DataEncodedImage(url=t['url'],
                                   width=t['width'],
                                   height=t['height'],
                                   mime='jpeg')
            for name, t in snippet['thumbnails'].items()}

    @classmethod
    def data_client(cls):
        return discovery.build(
            'youtube',
            'v3', developerKey=settings.YOUTUBE_DATA_API_KEY)

    @classmethod
    def dl_client(cls):
        dl = youtube_dl.YoutubeDL({
            'outtmpl': os.path.join(settings.YOUTUBE_DOWNLOAD_PATH,
                                    '%(title)s(%(id)s).%(ext)s'),
            'format': 'bestaudio',
            'quiet': True,
            'restrictfilenames': True,
        })
        dl.add_default_info_extractors()
        return dl

    @classmethod
    def get_url(cls, identifier):
        return cls.url.format(identifier)

    @classmethod
    def download(cls, identifier):
        url = cls.get_url(identifier)
        logger.debug("Downloading %s", url)
        dl_client = cls.dl_client()
        result = dl_client.extract_info(url, download=False)
        try:
            video = result['entries'][0]
        except KeyError:
            video = result
        info = dl_client.process_video_result(video)
        return dl_client.prepare_filename(info)

    @classmethod
    def search(cls, query):
        query = query.strip().lower()

        def search():
            logger.debug("Search for %s", query)
            client = cls.data_client()
            videos = client.search().list(q=query, type='video',
                                          part='id,snippet').execute()['items']
            ids = [video["id"]["videoId"] for video in videos]
            details = (client
                       .videos()
                       .list(id=','.join(ids), part='id,snippet,contentDetails')
                       .execute())['items']
            return [cls(obj) for obj in details]

        return cache.get_or_set('search/{}'.format(query),
                                search,
                                settings.YOUTUBE_SEARCH_CACHE_DURATION)

    def get_artist(self):
        return self.artist

    def get_title(self):
        return self.title

    def get_duration(self):
        return self.duration

    def get_identifier(self):
        return self.id

    def get_cover(self):
        return self.thumbnails['default'].content
