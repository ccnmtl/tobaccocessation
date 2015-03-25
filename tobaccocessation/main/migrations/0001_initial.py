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
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('gender', models.CharField(max_length=1, choices=[(b'-----', b'-----'), (b'M', b'Male'), (b'F', b'Female'), (b'D', b'Declined'), (b'U', b'Unavailable')])),
                ('is_faculty', models.CharField(max_length=2, choices=[(b'-----', b'-----'), (b'ST', b'Student'), (b'FA', b'Faculty'), (b'OT', b'Other')])),
                ('institute', models.CharField(max_length=2, choices=[(b'-----', b'-----'), (b'I1', b'Columbia University'), (b'I2', b'Jacobi Medical Center'), (b'I3', b'St. Barnabas Hospital'), (b'IF', b'Other')])),
                ('specialty', models.CharField(max_length=3, choices=[(b'-----', b'-----'), (b'S10', b'Dental Public Health'), (b'S3', b'Endodontics'), (b'S1', b'General Practice'), (b'S4', b'Oral and Maxillofacial Surgery'), (b'S5', b'Pediatric Dentistry'), (b'S6', b'Periodontics'), (b'S7', b'Prosthodontics'), (b'S2', b'Pre-Doctoral Student'), (b'S8', b'Orthodontics'), (b'S9', b'Other')])),
                ('hispanic_latino', models.CharField(max_length=1, choices=[(b'-----', b'-----'), (b'Y', b'Yes, Hispanic or Latino'), (b'N', b'No, not Hispanic or Latino'), (b'D', b'Declined'), (b'U', b'Unavailable/Unknown')])),
                ('race', models.CharField(max_length=2, choices=[(b'-----', b'-----'), (b'R1', b'American Indian or Alaska Native'), (b'R2', b'Asian'), (b'R3', b'Black or African American'), (b'R4', b'Native Hawaiian or other Pacific Islander'), (b'R5', b'White'), (b'R6', b'Some Other Race'), (b'R7', b'Declined'), (b'R8', b'Unavailable/Unknown')])),
                ('year_of_graduation', models.PositiveIntegerField(blank=True)),
                ('consent_participant', models.BooleanField(default=False)),
                ('consent_not_participant', models.BooleanField(default=False)),
                ('user', models.ForeignKey(related_name='application_user', to=settings.AUTH_USER_MODEL, unique=True)),
            ],
            options={
                'ordering': ['user'],
            },
            bases=(models.Model,),
        ),
    ]
