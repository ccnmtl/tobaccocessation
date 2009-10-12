from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from django.utils import simplejson

class Medication(models.Model):
    name = models.CharField(max_length=25)
    instructions = models.TextField()
    display_order = models.IntegerField()
    tag = models.CharField(max_length=25)
    
    def __unicode__(self):
        return "%s" % (self.name)
    
class ConcentrationChoice(models.Model):
    medication = models.ForeignKey(Medication)
    concentration = models.CharField(max_length=50)
    correct = models.BooleanField()
    display_order = models.IntegerField()
    
class DosageChoice(models.Model):
    medication = models.ForeignKey(Medication)
    dosage = models.CharField(max_length=50)
    correct = models.BooleanField()
    display_order = models.IntegerField()
    
class RefillChoice(models.Model):
    medication = models.ForeignKey(Medication)
    refill = models.CharField(max_length=50)
    correct = models.BooleanField()
    display_order = models.IntegerField()
    
class Patient(models.Model):
    name = models.CharField(max_length=25)
    description = models.TextField()
    history = models.TextField()
    display_order = models.IntegerField()
    
    def __unicode__(self):
        return "%s. %s" % (self.display_order, self.name)
    
class TreatmentClassification(models.Model):
    rank = models.IntegerField()
    description = models.CharField(max_length=50)
    
    def __unicode__(self):
        return "%s. %s" % (self.rank, self.description)
    
class TreatmentOption(models.Model):
    patient = models.ForeignKey(Patient)
    classification = models.ForeignKey(TreatmentClassification)
    medication_one = models.ForeignKey(Medication, related_name="medication_one")
    medication_two = models.ForeignKey(Medication, related_name="medication_two", blank=True, null=True)
    reasoning = models.TextField()
    
    def __unicode__(self):
        return "Option: %s [%s, %s]" % (self.classification.description, self.medication_one, self.medication_two)
    
class TreatmentFeedback(models.Model):
    patient = models.ForeignKey(Patient)
    classification = models.ForeignKey(TreatmentClassification)
    correct_dosage = models.BooleanField(blank=True)
    combination_therapy = models.BooleanField(blank=True) 
    feedback = models.TextField()
    
    def __unicode__(self):
        return "Feedback: %s %s" % (self.patient, self.classification.description)
    
class ActivityState (models.Model):
    user = models.ForeignKey(User, related_name="virtual_patient_user")
    json = models.TextField()