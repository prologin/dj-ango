import os
from unittest.case import SkipTest

from django.conf import settings

from dj.source.youtube import YouTube
from dj.tests import BaseTestCase


class TestSourceYouTube(BaseTestCase):
    def setUp(self):
        if not settings.YOUTUBE_DATA_API_KEY:
            raise SkipTest("No YOUTUBE_DATA_API_KEY defined")

    def test_url(self):
        identifier = 'dQw4w9WgXcQ'
        self.assertEqual(YouTube.get_url(identifier),
                         'https://youtube.com/watch?v=' + identifier)

    def test_search(self):
        results = YouTube.search("Rick Astley - Never Gonna Give You Up")
        self.assertTrue(results)
        first = results[0]
        self.assertEqual(first.get_identifier(), 'dQw4w9WgXcQ', msg="Wrong video ID")
        self.assertTrue(first.get_cover(), msg="Video has no thumbnail")
        self.assertIn('rick astley', first.get_artist().lower(), msg="Wrong artist")
        self.assertIn('never gonna give you up', first.get_title().lower(), msg="Wrong title")
        self.assertGreater(first.get_duration(), 60 * 3, msg="Video is not long enough")

    def test_download(self):
        with self.settings(YOUTUBE_FAKE_DOWNLOAD=False):
            results = YouTube.search("Rick Astley - Never Gonna Give You Up")
            first = results[0]
            filename = YouTube.download(first.get_identifier())
            self.assertTrue(filename, msg="Download filename is empty")
            self.assertTrue(os.path.exists(filename), msg="Download file does not exist")
            self.assertGreater(os.path.getsize(filename), 3000000, msg="Download file is not large enough")
