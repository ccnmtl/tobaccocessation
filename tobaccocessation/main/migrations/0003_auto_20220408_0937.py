# Generated by Django 3.2.12 on 2022-04-08 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20150612_1525'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='gender',
            field=models.CharField(choices=[('-----', '-----'), ('M', 'Male'), ('F', 'Female'), ('D', 'Declined'), ('U', 'Unavailable')], max_length=5),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='hispanic_latino',
            field=models.CharField(choices=[('-----', '-----'), ('Y', 'Yes, Hispanic or Latino'), ('N', 'No, not Hispanic or Latino'), ('D', 'Declined'), ('U', 'Unavailable/Unknown')], max_length=5),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='institute',
            field=models.CharField(choices=[('-----', '-----'), ('I1', 'Columbia University'), ('I2', 'Jacobi Medical Center'), ('I3', 'St. Barnabas Hospital'), ('IF', 'Other')], max_length=5),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='is_faculty',
            field=models.CharField(choices=[('-----', '-----'), ('ST', 'Student'), ('FA', 'Faculty'), ('OT', 'Other')], max_length=5),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='race',
            field=models.CharField(choices=[('-----', '-----'), ('R1', 'American Indian or Alaska Native'), ('R2', 'Asian'), ('R3', 'Black or African American'), ('R4', 'Native Hawaiian or other Pacific Islander'), ('R5', 'White'), ('R6', 'Some Other Race'), ('R7', 'Declined'), ('R8', 'Unavailable/Unknown')], max_length=5),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='specialty',
            field=models.CharField(choices=[('-----', '-----'), ('S10', 'Dental Public Health'), ('S3', 'Endodontics'), ('S1', 'General Practice'), ('S4', 'Oral and Maxillofacial Surgery'), ('S5', 'Pediatric Dentistry'), ('S6', 'Periodontics'), ('S7', 'Prosthodontics'), ('S2', 'Pre-Doctoral Student'), ('S8', 'Orthodontics'), ('S9', 'Other')], max_length=5),
        ),
    ]