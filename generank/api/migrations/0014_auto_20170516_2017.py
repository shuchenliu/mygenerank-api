# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-05-16 20:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_riskreductor_riskreductoroption'),
    ]

    operations = [
        migrations.AlterField(
            model_name='riskreductor',
            name='identifier',
            field=models.CharField(blank=True, max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='riskreductoroption',
            name='identifier',
            field=models.CharField(blank=True, max_length=100, unique=True),
        ),
    ]
