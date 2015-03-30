# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityState',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('json', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Block',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('medication_name', models.CharField(max_length=25)),
                ('allow_redo', models.BooleanField(default=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Medication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=25)),
                ('dosage', models.CharField(max_length=25)),
                ('dispensing', models.CharField(max_length=50)),
                ('signature', models.TextField()),
                ('refills', models.IntegerField()),
                ('sort_order', models.IntegerField()),
                ('dosage_callout', models.TextField(null=True, blank=True)),
                ('dispensing_callout', models.TextField(null=True, blank=True)),
                ('signature_callout', models.TextField(null=True, blank=True)),
                ('refills_callout', models.TextField(null=True, blank=True)),
                ('rx_count', models.IntegerField(default=1)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='activitystate',
            name='block',
            field=models.ForeignKey(to='activity_prescription_writing.Block'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='activitystate',
            name='user',
            field=models.ForeignKey(related_name='prescription_writing_user', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='activitystate',
            unique_together=set([('user', 'block')]),
        ),
    ]
