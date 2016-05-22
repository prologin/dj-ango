import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from django.core.urlresolvers import reverse_lazy

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SECRET_KEY = 'jow57y)c%)8dk2@+%^+__=7u7h)t5ez@*^#9x+l5z0j1@!zy9-'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'rules.apps.AutodiscoverRulesConfig',
    'dj.apps.DjAppConfig',
    'django_prometheus',
]

MIDDLEWARE_CLASSES = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': True,
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'dj.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'dj_ango',
        'USER': 'dj_ango',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'dj-cache',
    }
}
# Cache key prefix
KEY_PREFIX = 'dj/'

STATIC_URL = '/static/'

ROOT_URLCONF = 'urls'

CRISPY_TEMPLATE_PACK = 'bootstrap3'

LOGIN_URL = reverse_lazy('dj:login')
LOGIN_REDIRECT_URL = reverse_lazy('dj:home')

AUTHENTICATION_BACKENDS = [
    'rules.permissions.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# mpd daemon address for remote control
MPD_ADDRESS = ('localhost', 6600)
# mpd root music directory
MPD_MUSIC_ROOT = '/tmp/dj_ango/mpdroot'
# YouTube Data API key
YOUTUBE_DATA_API_KEY = ''
# Youtube downloads destionation directory
YOUTUBE_DOWNLOAD_PATH = os.path.join(MPD_MUSIC_ROOT, 'youtube')
# Cache time to live in seconds
YOUTUBE_SEARCH_CACHE_DURATION = 3600
# If True, YouTube.download() does not actually download the video
# (useful for testing)
YOUTUBE_FAKE_DOWNLOAD = False
