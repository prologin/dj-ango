from django.conf.urls.defaults import *

urlpatterns = patterns('DJ_Ango.dj.views',
    url(r'^/?$', 'index', name='dj.index'),
    url(r'^vote/(\d+)/?$', 'vote', name='dj.vote'),
    url(r'^add/?', 'add', name='dj.add'),
    url(r'^validate/?', 'validate', name='dj.validate'),
    url(r'^login/?', 'login', name='dj.login'),
    url(r'^logout/?', 'logout', name='dj.logout'),
)
