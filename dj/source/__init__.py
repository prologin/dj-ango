import base64
import urllib

from django.core import signing
from django.utils.functional import cached_property

from dj.templatetags.djutils import elapsed


def all():
    return SongSourceRegistry.registry.values()


def from_code(code):
    return SongSourceRegistry.registry[code]


class SongSourceRegistry(type):
    registry = {}

    def __new__(cls, clsname, bases, attrs):
        newclass = super().__new__(cls, clsname, bases, attrs)
        if newclass.source_code:
            cls.registry[newclass.source_code] = newclass
        return newclass


class SongSource(metaclass=SongSourceRegistry):
    source_code = None
    source_icon = None
    source_name = None

    @classmethod
    def load(cls, opaque: str, song) -> dict:
        """
        Loads state from an signed opaque string.
        """
        state = signing.loads(opaque)
        for attr, value in state.items():
            setattr(song, attr, value)

    @classmethod
    def get_url(cls, identifier: str) -> str:
        """
        Returns the upstream song URL of the given upstream identifier.
        """
        raise NotImplementedError()

    @classmethod
    def download(cls, identifier: str) -> str:
        """
        Downloads the upstream song of the given upstream identifier and returns
        the stored filename.
        """
        raise NotImplementedError()

    @classmethod
    def search(cls, query):
        """
        Returns a list of upstream songs matching `query`.
        """
        raise NotImplementedError()

    def artist_and_name(self):
        artist = self.get_artist()
        return "".join([artist + " – " if artist else "", self.get_title()])

    def get_artist(self):
        """
        Returns the song artist.
        """
        raise NotImplementedError()

    def get_title(self):
        """
        Returns the song title.
        """
        raise NotImplementedError()

    def get_cover(self):
        """
        Returns this song cover picture (data: format), if available, else None.
        """
        raise NotImplementedError()

    def get_duration(self) -> int:
        """
        Returns this song duration.
        :return:
        """
        raise NotImplementedError()

    def get_identifier(self) -> str:
        """
        Returns this song upstream identifier.
        """
        raise NotImplementedError()

    def dump(self) -> str:
        """
        Returns a signed dump of the state, to be read back using `load()`.
        """
        return signing.dumps({
            'source': self.source_code,
            'duration': self.get_duration(),
            'identifier': self.get_identifier(),
        })

    def __repr__(self):
        return "<SongSource [{}] {} - {} ({})>".format(
            self.get_identifier(), self.get_artist() or "Unknown", self.get_title(),
            elapsed(self.get_duration()))


class DataEncodedImage:
    def __init__(self, url, width, height, mime):
        self.url = url
        self.width = width
        self.height = height
        self.mime = mime

    @cached_property
    def content(self):
        with urllib.request.urlopen(self.url) as response:
            return 'data:image/{};base64,{}'.format(
                self.mime, base64.b64encode(response.read()).decode())
