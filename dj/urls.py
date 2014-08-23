from django.conf.urls.defaults import *

urlpatterns = patterns('DJ_Ango.dj.views',
    url(r'^/?$', 'index', name='DJ_Ango.dj.index'),
    url(r'^now_playing/?$', 'now_playing', name='DJ_Ango.dj.now_playing'),
    url(r'^next/?$', 'next', name='DJ_Ango.dj.next'),
    url(r'^vote/(\d+)/?$', 'vote', name='DJ_Ango.dj.vote'),
    url(r'^vote/add/(\d+)/?$', 'add_vote', name='DJ_Ango.dj.add_vote'),
    url(r'^vote/rm/(\d+)/?$', 'del_vote', name='DJ_Ango.dj.del_vote'),
    url(r'^vote/([a-z]+)/(\d+)/?$', 'vote_category', name='DJ_Ango.dj.vote_category'),
    url(r'^vote/get_([a-z]+)/(\d+)/?$', 'vote_get_category', name='DJ_Ango.dj.vote_get_category'),
    url(r'^add/?', 'add', name='DJ_Ango.dj.add'),
    url(r'^validate/?', 'validate', name='DJ_Ango.dj.validate'),
    url(r'^login/?', 'login', name='DJ_Ango.dj.login'),
    url(r'^logout/?', 'logout', name='DJ_Ango.dj.logout'),
)
