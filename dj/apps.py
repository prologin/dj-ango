import traceback
from django.apps import AppConfig
from django.conf import settings
from django.core.checks import register, Error

from dj.youtube import YouTube


@register
def check_youtube_api(app_configs, **kwargs):
    if not settings.YOUTUBE_DATA_API_KEY:
        return [Error("YOUTUBE_DATA_API_KEY not defined.", id="dj.E001")]
    try:
        youtube = YouTube()
        assert youtube.search('alejandro')
    except Exception:
        return [Error(
            "Invalid YOUTUBE_DATA_API_KEY or YouTube Data API is broken.",
            id="dj.E002",
            hint="\n" + traceback.format_exc())]
    return []


class DjAppConfig(AppConfig):
    name = "dj"
