# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-23 03:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ActualFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cid', models.CharField(default='', max_length=128)),
                ('fid', models.CharField(max_length=128, unique=True)),
                ('path', models.TextField()),
                ('ftype', models.IntegerField()),
                ('inode', models.IntegerField(default=0)),
                ('links', models.IntegerField(default=0)),
                ('check_sum', models.CharField(max_length=1024)),
                ('uid', models.IntegerField(default=0)),
                ('user', models.CharField(default='', max_length=64)),
                ('gid', models.IntegerField(default=0)),
                ('group', models.CharField(default='', max_length=64)),
                ('mode', models.IntegerField(default=0)),
                ('ctime', models.DateTimeField()),
                ('atime', models.DateTimeField()),
                ('mtime', models.DateTimeField()),
                ('adtime', models.DateTimeField(auto_now_add=True)),
                ('cktime', models.DateTimeField(auto_now=True)),
                ('status', models.IntegerField(default=0)),
                ('remark', models.IntegerField(default='')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BaseLineFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cid', models.CharField(default='', max_length=128)),
                ('fid', models.CharField(max_length=128, unique=True)),
                ('path', models.TextField()),
                ('ftype', models.IntegerField()),
                ('inode', models.IntegerField(default=0)),
                ('links', models.IntegerField(default=0)),
                ('check_sum', models.CharField(max_length=1024)),
                ('uid', models.IntegerField(default=0)),
                ('user', models.CharField(default='', max_length=64)),
                ('gid', models.IntegerField(default=0)),
                ('group', models.CharField(default='', max_length=64)),
                ('mode', models.IntegerField(default=0)),
                ('ctime', models.DateTimeField()),
                ('atime', models.DateTimeField()),
                ('mtime', models.DateTimeField()),
                ('btime', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(default='')),
                ('adtime', models.DateTimeField(auto_now_add=True)),
                ('dltime', models.DateTimeField(auto_now=True)),
                ('status', models.IntegerField(default=0)),
                ('remark', models.IntegerField(default='')),
            ],
        ),
    ]