import youtube_dl
import os.path

from django.conf import settings
from googleapiclient import discovery


class YouTube:
    def __init__(self):
        self.client = discovery.build(
            'youtube',
            'v3', developerKey=settings.YOUTUBE_DATA_API_KEY)
        self.dl = youtube_dl.YoutubeDL({
            'outtmpl': os.path.join(settings.YOUTUBE_DOWNLOAD_PATH,
                                    '%(title)s(%(id)s).%(ext)s'),
            'format': 'bestaudio',
            'quiet': True,
            'restrictfilenames': True,
        })
        self.dl.add_default_info_extractors()

    def search(self, query, **kwargs):
        return (self.client.search().list(q=query,
                                          type='video',
                                          part='id,snippet',
                                          **kwargs).execute())['items']

    def details(self, ids):
        return (self.client.videos().list(
            id=','.join(ids),
            part='id,snippet,contentDetails').execute())['items']

    def download_audio(self, url):
        result = self.dl.extract_info(url, download=False)
        if 'entries' in result:
            video = result['entries'][0]
        else:
            video = result
        info = self.dl.process_video_result(video)
        info['filename'] = os.path.basename(self.dl.prepare_filename(info))
        return info
