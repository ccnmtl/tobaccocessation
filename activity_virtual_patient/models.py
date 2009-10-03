from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from django.utils import simplejson

class Medication(models.Model):
    name = models.CharField(max_length=25)
    instructions = models.TextField()
    
    def __unicode__(self):
        return "%s" % (self.name)
    
class MedicationConcentrationChoice(models.Model):
    medication = models.ForeignKey(Medication)
    concentration = models.CharField(max_length=50)
    correct = models.BooleanField(),
    display_order = models.IntegerField()
    
class MedicationDosageChoice(models.Model):
    medication = models.ForeignKey(Medication)
    dosage = models.CharField(max_length=50)
    correct = models.BooleanField(),
    display_order = models.IntegerField()
    
class MedicationRefillChoice(models.Model):
    medication = models.ForeignKey(Medication)
    refill = models.CharField(max_length=50)
    correct = models.BooleanField(),
    display_order = models.IntegerField()