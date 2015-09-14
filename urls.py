from django.conf.urls import patterns, include, url
from django.contrib import admin
from dj import views

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^/?$', views.index, name='dj.index'),
    url(r'^now_playing/?$', views.now_playing, name='dj.now_playing'),
    url(r'^next/?$', views.next, name='dj.next'),
    url(r'^vote/(\d+)/?$', views.vote, name='dj.vote'),
    url(r'^vote/add/?$', views.add_vote, name='dj.add_vote'),
    url(r'^vote/rm/?$', views.del_vote, name='dj.del_vote'),
    url(r'^vote/([a-z]+)/(\d+)/?$', views.vote_category, name='dj.vote_category'),
    url(r'^vote/get_([a-z]+)/(\d+)/?$', views.vote_get_category, name='dj.vote_get_category'),
    url(r'^add/?$', views.add , name='dj.add'),
    url(r'^add/pending/?$', views.user_pending, name='dj.user_pending'),
    url(r'^search/(.+)/?$', views.add_results, name='dj.add_results'),
    url(r'^add_pending/?$', views.add_pending, name='dj.add_pending'),
    url(r'^add_upload/?$', views.add_upload, name='dj.add_upload'),
    url(r'^validate/?$', views.validate, name='dj.validate'),
    url(r'^pending/?$', views.pending, name='dj.pending'),
    url(r'^validate/(\d+)/?$', views.validate_pending, name='dj.validate_pending'),
    url(r'^nuke/(\d+)/?$', views.nuke_pending, name='dj.nuke_pending'),
    url(r'^login/?$', views.login, name='dj.login'),
    url(r'^logout/?$', views.logout, name='dj.logout'),
    url('', include('django_prometheus.urls')),
)
