from django.conf.urls import url
import django.contrib.auth.views

from dj import views

urlpatterns = [
    url(r'^$', views.HomeView.as_view(),
        name='home'),
    url(r'^vote$', views.VoteSongView.as_view(),
        name='vote'),
    url(r'^login$', views.LoginView.as_view(),
        name='login'),
    url(r'^logout$',
        django.contrib.auth.views.logout_then_login,
        name='logout'),
    url(r'^suggest$',
        views.SuggestSongView.as_view(),
        name='suggest'),
    url(r'^validate$',
        views.ValidateSongView.as_view(),
        name='validate'),

    # Stubs
    url(r'^stub/now-playing$',
        views.NowPlayingStubView.as_view(),
        name='stub-now-playing'),
    url(r'^stub/playing-next$',
        views.PlayingNextStubView.as_view(),
        name='stub-playing-next'),

    # Player control
    url(r'^volume$', views.VolumeView.as_view(),
        name='volume'),
    url(r'^skip$', views.SkipSongView.as_view(),
        name='skip'),
]
