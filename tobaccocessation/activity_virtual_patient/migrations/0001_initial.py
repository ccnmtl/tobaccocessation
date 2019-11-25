# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('pagetree', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityState',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('json', models.TextField()),
                ('hierarchy', models.ForeignKey(to='pagetree.Hierarchy', on_delete=models.CASCADE)),
                ('user', models.ForeignKey(related_name='virtual_patient_user', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ConcentrationChoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('concentration', models.CharField(max_length=50)),
                ('correct', models.BooleanField(default=False)),
                ('display_order', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DosageChoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dosage', models.CharField(max_length=50)),
                ('correct', models.BooleanField(default=False)),
                ('display_order', models.IntegerField()),
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
                ('instructions', models.TextField()),
                ('display_order', models.IntegerField()),
                ('tag', models.CharField(max_length=25)),
                ('rx_count', models.IntegerField(default=1)),
            ],
            options={
                'ordering': ['display_order'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=25)),
                ('description', models.TextField()),
                ('history', models.TextField()),
                ('display_order', models.IntegerField()),
                ('gender', models.CharField(default=b'F', max_length=1, choices=[(b'F', b'Female'), (b'M', b'Male')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PatientAssessmentBlock',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('view', models.IntegerField(choices=[(0, b'Treatment Options'), (1, b'Best Treatment Option'), (2, b'Prescription'), (3, b'Results')])),
                ('patient', models.ForeignKey(to='activity_virtual_patient.Patient', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RefillChoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('refill', models.CharField(max_length=50)),
                ('correct', models.BooleanField(default=False)),
                ('display_order', models.IntegerField()),
                ('medication', models.ForeignKey(to='activity_virtual_patient.Medication', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TreatmentClassification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rank', models.IntegerField()),
                ('description', models.CharField(max_length=50)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TreatmentFeedback',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('correct_dosage', models.BooleanField(default=False)),
                ('combination_therapy', models.BooleanField(default=False)),
                ('feedback', models.TextField()),
                ('classification', models.ForeignKey(to='activity_virtual_patient.TreatmentClassification', on_delete=models.CASCADE)),
                ('patient', models.ForeignKey(to='activity_virtual_patient.Patient', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TreatmentOption',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('classification', models.ForeignKey(to='activity_virtual_patient.TreatmentClassification', on_delete=models.CASCADE)),
                ('medication_one', models.ForeignKey(related_name='medication_one', to='activity_virtual_patient.Medication', on_delete=models.CASCADE)),
                ('medication_two', models.ForeignKey(related_name='medication_two', blank=True, to='activity_virtual_patient.Medication', null=True, on_delete=models.CASCADE)),
                ('patient', models.ForeignKey(to='activity_virtual_patient.Patient', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TreatmentOptionReasoning',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('combination', models.BooleanField()),
                ('reasoning', models.TextField()),
                ('display_order', models.IntegerField(default=0)),
                ('classification', models.ForeignKey(to='activity_virtual_patient.TreatmentClassification', on_delete=models.CASCADE)),
                ('medication', models.ForeignKey(blank=True, to='activity_virtual_patient.Medication', null=True, on_delete=models.CASCADE)),
                ('patient', models.ForeignKey(to='activity_virtual_patient.Patient', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['display_order', 'id'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='dosagechoice',
            name='medication',
            field=models.ForeignKey(to='activity_virtual_patient.Medication', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='concentrationchoice',
            name='medication',
            field=models.ForeignKey(to='activity_virtual_patient.Medication', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='activitystate',
            unique_together=set([('user', 'hierarchy')]),
        ),
    ]
