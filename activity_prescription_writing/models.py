from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from django.utils import simplejson
from django.contrib.contenttypes import generic
from pagetree.models import PageBlock
from django import forms

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
    rx_count = models.IntegerField(default=1)
    
    def __unicode__(self):
        return "%s" % (self.name)

class Block(models.Model):
    pageblocks = generic.GenericRelation(PageBlock, related_name="prescription_writing_pageblocks")
    medication_name = models.CharField(max_length=25)
    show_correct = models.BooleanField(default=False)
    template_file = "activity_prescription_writing/prescription.html"
    display_name = "Activity: Prescription Writing"
    
    def pageblock(self):
        return self.pageblocks.all()[0]

    def __unicode__(self):
        return unicode(self.pageblock())

    def needs_submit(self):
        return False
    
    def unlocked(self,user):
        return True
    
    @classmethod
    def add_form(self):
        class AddForm(forms.Form):
            medication_name = forms.CharField()
            show_correct = forms.BooleanField()
        return AddForm()

    @classmethod
    def create(self,request):
        name = request.POST.get('medication_name','')
        show_correct = request.POST.get('show_correct', '')
        return Block.objects.create(medication_name=name, show_correct=show_correct)
    
    def edit_form(self):
        class EditForm(forms.Form):
            medication_name = forms.CharField(initial=self.medication_name)
            show_correct = forms.BooleanField(initial=self.show_correct)
        return EditForm();
    
    def edit(self,vals,files):
        medication_name = vals.get('medication_name','')
        show_correct = vals.get('show_correct', '') 
        self.save()
        
    def medication(self):
        return Medication.objects.filter(name=self.medication_name).order_by('id')
    
    
class ActivityState (models.Model):
    user = models.ForeignKey(User, related_name="prescription_writing_user")
    json = models.TextField(blank=True)


    
