import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DJ_Ango.settings")

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
