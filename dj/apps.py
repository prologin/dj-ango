import traceback
from django.apps import AppConfig
from django.core.checks import register, Error


@register
def check_youtube_api(app_configs, **kwargs):
    from dj.source.youtube import YouTube
    try:
        assert YouTube.search('alejandro')
    except Exception:
        return [Error(
            "Invalid YOUTUBE_DATA_API_KEY or YouTube Data API is broken.",
            id="dj.E001",
            hint="\n" + traceback.format_exc())]
    return []


class DjAppConfig(AppConfig):
    name = "dj"
