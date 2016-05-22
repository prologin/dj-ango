import logging
import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, REDIRECT_FIELD_NAME
from django.core.exceptions import SuspiciousOperation
from django.core.signing import BadSignature
from django.core.urlresolvers import reverse_lazy, reverse
from django.db import IntegrityError
from django.db import transaction
from django.db.models import Q
from django.http.response import HttpResponseBadRequest, HttpResponseRedirect, \
    HttpResponse
from django.shortcuts import redirect, resolve_url
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.utils.html import format_html
from django.utils.http import is_safe_url
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View, ListView
from django.views.generic.edit import FormView, CreateView, UpdateView, \
    ModelFormMixin
from rules.contrib.views import PermissionRequiredMixin

import dj.forms
import dj.models
import dj.player
import dj.source

logger = logging.getLogger('dj.views')


def validate_download_song(pending_song):
    with transaction.atomic():
        cls = dj.source.from_code(pending_song.source)
        path = cls.download(pending_song.identifier)
        path = os.path.relpath(path, settings.MPD_MUSIC_ROOT)
        song = dj.models.Song(artist=pending_song.artist,
                              title=pending_song.title,
                              duration=pending_song.duration,
                              path=path)
        song.save()
        if pending_song.pk is not None:
            pending_song.delete()
    return song


class HomeView(PermissionRequiredMixin, ListView):
    template_name = "dj/index.html"
    model = dj.models.Song
    next_count = 5
    context_object_name = 'songs'
    permission_required = "dj.browse"

    def get_queryset(self):
        return super().get_queryset()[:self.next_count]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        player = dj.models.Player.instance()
        if player.is_playing():
            context['current_song'] = player.song
            context['current_elapsed'] = timezone.now() - player.start_time
        context['volume'] = dj.player.get_volume()
        return context


class VoteSongListView(ListView):
    # Permission checking is done in VoteSongView
    template_name = 'dj/vote.html'
    model = dj.models.Song
    context_object_name = 'songs'
    paginate_by = 20

    @cached_property
    def search_query(self):
        return self.request.GET.get('q', '').strip()

    def get_queryset(self):
        qs = super().get_queryset().prefetch_related('votes')
        query = self.search_query
        if query:
            qs = qs.filter(Q(title__icontains=query) | Q(
                artist__icontains=query))
        return qs


class VoteOrUnvoteSongView(UpdateView):
    # Permission checking is done in VoteSongView
    model = dj.models.Song
    fields = []

    def get_success_url(self):
        return self.request.POST['next']

    def get_object(self, queryset=None):
        return (queryset or self.get_queryset()).get(
            pk=self.request.POST['song_id'])

    def form_invalid(self, form):
        return HttpResponseBadRequest()

    def form_valid(self, form):
        try:
            method = self.request.POST['action']
            if method not in ('add', 'remove'):
                raise AttributeError()
            getattr(self.object.votes, method)(self.request.user)
            return super(ModelFormMixin, self).form_valid(form)
        except Exception:
            return HttpResponseBadRequest()


class VoteSongView(PermissionRequiredMixin, View):
    permission_required = 'dj.vote_song'

    def get(self, request, *args, **kwargs):
        return VoteSongListView.as_view()(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return VoteOrUnvoteSongView.as_view()(request, *args, **kwargs)


class SuggestSongView(PermissionRequiredMixin, CreateView):
    template_name = 'dj/suggest.html'
    model = dj.models.PendingSong
    queryset = model.objects.filter(banned=False)
    fields = ['artist', 'title']
    context_object_name = 'songs'
    pending_song_count = 5
    success_url = reverse_lazy('dj:suggest')
    permission_required = 'dj.suggest_song'

    @cached_property
    def search_query(self):
        return self.request.GET.get('q', '').strip().lower()

    def get_success_url(self):
        if self.search_query:
            return '{}?q={}'.format(self.success_url, self.search_query)
        return self.success_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Source list
        context['available_sources'] = [source.source_name
                                        for source in dj.source.all()]
        # Add a few songs from pending songs
        context['pending_songs'] = self.get_queryset()[:
                                                       self.pending_song_count]
        # Execute search if needed
        q = self.search_query
        if q:
            search_results = []
            for source in dj.source.all():
                search_results.extend(source.search(q))
            context['search_results'] = search_results
        return context

    def form_valid(self, form):
        # Save new suggestion (or error out if banned)
        pending_song = self.object = form.save(commit=False)
        pending_song.submitter = self.request.user
        try:
            dj.source.SongSource.load(self.request.POST['state'], pending_song)
        except KeyError:
            return HttpResponseBadRequest()
        except BadSignature:
            return SuspiciousOperation("Malformed SerializableSong state")
        try:
            if self.request.user.has_perm(
                    'dj.validate_song') and self.request.POST.get(
                        'instant_validate'):
                messages.success(self.request,
                                 format_html("{} was added and validated.",
                                             pending_song))
                validate_download_song(pending_song)
            else:
                with transaction.atomic():
                    pending_song.save()
                messages.success(self.request, format_html(
                    "{} was added to validation queue.", pending_song))
            return super(ModelFormMixin, self).form_valid(form)
        except IntegrityError:
            banned = self.model.objects.filter(
                identifier=pending_song.identifier,
                banned=True).exists()
            if banned:
                form.add_error(None, "This song is banned from suggestions.")
            else:
                form.add_error(None,
                               "This song is already pending validation.")
            return self.form_invalid(form)


class ValidateSongView(PermissionRequiredMixin, View):
    permission_required = 'dj.validate_song'

    def get(self, request, *args, **kwargs):
        return ValidateSongListView.as_view()(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return ValidateOrNukeSongView.as_view()(request, *args, **kwargs)


class ValidateSongListView(ListView):
    # Permission checking is done in ValidateSongView
    template_name = 'dj/validate.html'
    model = dj.models.PendingSong
    context_object_name = 'pending_songs'
    paginate_by = 20


class ValidateOrNukeSongView(UpdateView):
    # Permission checking is done in ValidateSongView
    model = dj.models.PendingSong
    fields = ['artist', 'title']
    success_url = reverse_lazy('dj:validate')

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        return queryset.get(pk=self.request.POST['song_id'])

    def form_invalid(self, form):
        print(form.errors)
        return redirect(reverse('dj:validate'))

    def form_valid(self, form):
        try:
            decision = self.request.POST['decision']
            self.object = form.save(commit=False)
            if decision == 'ban':
                if self.object.banned:
                    return HttpResponseBadRequest()
                else:
                    self.object.banned = True
                    self.object.save()
            elif decision == 'unban':
                if self.object.banned:
                    self.object.banned = False
                    self.object.save()
                else:
                    return HttpResponseBadRequest()
            elif decision == 'validate':
                validate_download_song(self.object)
            elif decision == 'nuke':
                self.object.delete()
            return super(ModelFormMixin, self).form_valid(form)
        except KeyError:
            return HttpResponseBadRequest()


class LoginView(FormView):
    template_name = 'dj/login.html'
    form_class = dj.forms.DjAuthenticationForm
    redirect_field_name = REDIRECT_FIELD_NAME

    def form_valid(self, form):
        redirect_to = self.request.POST.get(self.redirect_field_name,
                                            self.request.GET.get(
                                                self.redirect_field_name, ''))
        user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])
        if user is not None:
            login(self.request, user)
            if not is_safe_url(url=redirect_to, host=self.request.get_host()):
                redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)
            login(self.request, form.get_user())
            return HttpResponseRedirect(redirect_to)


class SkipSongView(PermissionRequiredMixin, View):
    url = reverse_lazy('dj:home')
    permission_required = 'dj.skip_song'

    def post(self, request, *args, **kwargs):
        dj.player.skip()
        return redirect(self.url)


@method_decorator(csrf_exempt, name='dispatch')
class VolumeView(PermissionRequiredMixin, View):
    permission_required = 'dj.set_volume'

    def get(self, request, *args, **kwargs):
        return HttpResponse(str(dj.player.get_volume()))

    def post(self, request, *args, **kwargs):
        try:
            dj.player.set_volume(int(self.request.body[:3].decode()))
            return HttpResponse(status=204)
        except ValueError:
            return HttpResponseBadRequest()


class NowPlayingStubView(HomeView):
    template_name = 'dj/index_stub_now_playing.html'


class PlayingNextStubView(HomeView):
    template_name = 'dj/index_stub_playing_next.html'
