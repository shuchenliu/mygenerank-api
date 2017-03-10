# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-02-21 23:08
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_auto_20170221_2239'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ancestry',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ancestry', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='ancestry',
            unique_together=set([('user', 'population')]),
        ),
    ]