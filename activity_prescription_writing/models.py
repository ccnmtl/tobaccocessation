from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from django.utils import simplejson

class Medication(models.Model):
    name = models.CharField(max_length=25)
    dosage = models.CharField(max_length=25)
    dispensing = models.CharField(max_length=50)
    signature = models.TextField()
    refills = models.IntegerField()
    sort_order = models.IntegerField()
    dosage_callout = models.TextField(blank=True, null=True)
    dispensing_callout = models.TextField(blank=True, null=True)
    signature_callout = models.TextField(blank=True, null=True)
    refills_callout = models.TextField(blank=True, null=True)
    
    def __unicode__(self):
        return "%s" % (self.name)

class ActivityState (models.Model):
    user = models.ForeignKey(User, related_name="prescription_writing_user")
    json = models.TextField(blank=True)


    
