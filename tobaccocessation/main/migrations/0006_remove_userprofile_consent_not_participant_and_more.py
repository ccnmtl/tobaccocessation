# Generated by Django 4.2.16 on 2024-10-07 14:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_reintroduce_consent'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='consent_not_participant',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='consent_participant',
        ),
    ]
