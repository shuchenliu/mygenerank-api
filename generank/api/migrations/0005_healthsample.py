# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-02-15 23:12
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20170202_2055'),
    ]

    operations = [
        migrations.CreateModel(
            name='HealthSample',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('identifier', models.CharField(blank=True, max_length=100)),
                ('value', models.FloatField(blank=True, max_length=100)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('collected_date', models.DateTimeField(default=datetime.datetime.now)),
                ('units', models.CharField(blank=True, max_length=100)),
                ('user', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='health_samples', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]