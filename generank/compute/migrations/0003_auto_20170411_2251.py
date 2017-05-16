# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-04-11 22:51
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('compute', '0002_auto_20170411_2249'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskstatus',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='task_statuses', to=settings.AUTH_USER_MODEL),
        ),
    ]
