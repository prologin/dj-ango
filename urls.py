from django.conf.urls import include
from django.conf.urls import url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('dj.urls', namespace='dj')),
    url(r'', include('django_prometheus.urls')),
]
