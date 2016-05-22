# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-18 15:54
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_prometheus.models


def create_player_object(apps, schema_editor):
    Player = apps.get_model('dj.Player')
    Player().save()


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PendingSong',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('banned', models.BooleanField(default=False, help_text='Any further submissions of this song will be automatically nuked.', verbose_name='Banned')),
                ('title', models.CharField(max_length=256, verbose_name='Title')),
                ('artist', models.CharField(max_length=256, verbose_name='Artist', blank=True)),
                ('duration', models.IntegerField(verbose_name='Duration', help_text='In seconds.')),
                ('source', models.CharField(max_length=16, verbose_name='Source')),
                ('identifier', models.CharField(max_length=256, verbose_name='Identifier')),
                ('submitter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submitted_songs', to=settings.AUTH_USER_MODEL, verbose_name='Submitter')),
            ],
            bases=(django_prometheus.models.ExportModelOperationsMixin('pending_song'), models.Model),
            options={'ordering': ('banned', '-id'), 'unique_together': set([('source', 'identifier')])},
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField(blank=True, null=True, verbose_name='Current song starting time')),
            ],
        ),
        migrations.CreateModel(
            name='Song',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256, verbose_name='Title')),
                ('artist', models.CharField(max_length=256, verbose_name='Artist', blank=True)),
                ('path', models.CharField(max_length=512, unique=True, verbose_name='Path to file')),
                ('duration', models.IntegerField(verbose_name='Duration', help_text='In seconds.')),
                ('votes', models.ManyToManyField(blank=True, related_name='voted_songs', to=settings.AUTH_USER_MODEL, verbose_name='Votes by users')),
            ],
            bases=(django_prometheus.models.ExportModelOperationsMixin('song'), models.Model),
        ),
        migrations.AddField(
            model_name='player',
            name='song',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='dj.Song', verbose_name='Current song'),
        ),
        migrations.RunPython(create_player_object, migrations.RunPython.noop),
    ]
