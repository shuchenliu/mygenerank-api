# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-08-15 21:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0023_auto_20170803_2159'),
    ]

    operations = [
        migrations.AddField(
            model_name='condition',
            name='risk_profile_title',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
