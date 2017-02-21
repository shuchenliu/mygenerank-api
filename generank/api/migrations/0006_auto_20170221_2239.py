# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-02-21 22:39
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_healthsample'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ancestry',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('value', models.FloatField(blank=True, default=-1.0, max_length=100)),
                ('population', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Population')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='ancestry', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='healthsample',
            name='collected_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='riskscore',
            name='created_on',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterUniqueTogether(
            name='healthsample',
            unique_together=set([('user', 'identifier', 'value', 'start_date', 'end_date', 'units')]),
        ),
    ]
