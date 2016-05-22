from unittest.case import SkipTest

import mpd

import dj.player
from dj.tests import BaseTestCase


class TestPlayer(BaseTestCase):
    def setUp(self):
        try:
            with dj.player.mpd_client():
                pass
        except mpd.ConnectionError:
            raise SkipTest("mpd is not up")

    def test_volume(self):
        for volume in (0, 20, 50, 99, 100):
            dj.player.set_volume(volume)
            self.assertEqual(dj.player.get_volume(cached=False), volume)
