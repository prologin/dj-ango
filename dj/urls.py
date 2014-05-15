from django.conf.urls.defaults import *

urlpatterns = patterns('DJ_Ango.dj.views',
    url(r'^/?$', 'index', name='DJ_Ango.dj.index'),
    url(r'^vote/(\d+)/?$', 'vote', name='DJ_Ango.dj.vote'),
    url(r'^add/?', 'add', name='DJ_Ango.dj.add'),
    url(r'^validate/?', 'validate', name='DJ_Ango.dj.validate'),
    url(r'^login/?', 'login', name='DJ_Ango.dj.login'),
    url(r'^logout/?', 'logout', name='DJ_Ango.dj.logout'),
)
