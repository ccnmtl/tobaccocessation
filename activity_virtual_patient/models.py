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
    correct = models.BooleanField()
    display_order = models.IntegerField()
    
class MedicationDosageChoice(models.Model):
    medication = models.ForeignKey(Medication)
    dosage = models.CharField(max_length=50)
    correct = models.BooleanField()
    display_order = models.IntegerField()
    
class MedicationRefillChoice(models.Model):
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
    
    